import os
import tempfile
import time
import subprocess
import uuid
import shutil
import logging
import threading
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PY_IMAGE = "codefarm-python:3.11"

MAX_STDOUT_SIZE = 1 * 1024 * 1024  # 1MB
MAX_STDERR_SIZE = 1 * 1024 * 1024  # 1MB
READ_CHUNK_SIZE = 4096


def indent_user_code(code: str) -> str:
    return "\n".join("    " + line for line in code.splitlines())


def _docker_exec_read_int(container_name: str, path: str) -> int | None:
    """
    docker exec로 컨테이너 내부 파일을 읽어 정수로 파싱.
    실패 시 None.
    """
    r = subprocess.run(
        ["docker", "exec", container_name, "cat", path],
        capture_output=True,
        text=True,
        timeout=0.5,
    )
    if r.returncode != 0:
        return None

    s = r.stdout.strip()
    if not s:
        return None

    # cgroup v2에서 memory.max 같은 파일은 "max"가 나올 수 있음
    if s == "max":
        return None

    try:
        return int(s)
    except:
        return None


def read_cgroup_memory_current_bytes(container_name: str) -> int:
    """
    컨테이너 내부에서 cgroup memory current(바이트)를 읽음.
    v2/v1 모두 대응. 못 읽으면 0.
    """
    # cgroup v2
    v2 = _docker_exec_read_int(container_name, "/sys/fs/cgroup/memory.current")
    if v2 is not None:
        return v2

    # cgroup v1
    v1 = _docker_exec_read_int(container_name, "/sys/fs/cgroup/memory/memory.usage_in_bytes")
    if v1 is not None:
        return v1

    return 0


def read_cgroup_memory_peak_bytes(container_name: str) -> int | None:
    """
    컨테이너 내부에서 cgroup peak(바이트)를 읽음.
    있으면 반환, 없으면 None.
    """
    # cgroup v2 (있을 때만)
    v2 = _docker_exec_read_int(container_name, "/sys/fs/cgroup/memory.peak")
    if v2 is not None:
        return v2

    # cgroup v1
    v1 = _docker_exec_read_int(container_name, "/sys/fs/cgroup/memory/memory.max_usage_in_bytes")
    if v1 is not None:
        return v1

    return None


def run_python_in_docker(code: str, stdin: str, time_limit_ms: int, mem_mb: int, cpu_limit: float):
    tmp = tempfile.mkdtemp(prefix="codefarm_", dir="/tmp")
    container_name = f"codefarm-run-{uuid.uuid4().hex[:12]}"

    wrapped_code = f"""
import time
import json

__cf_start = time.perf_counter()
try:
{indent_user_code(code)}
except Exception:
    raise
__cf_end = time.perf_counter()

print("\\n__CF_TIME__=" + json.dumps({{"time_ms": int((__cf_end-__cf_start)*1000)}}))
"""

    stop_monitor = threading.Event()
    peak_mem_kb = 0
    monitor_started = threading.Event()

    def monitor_memory():
        nonlocal peak_mem_kb

        # 최소 1회 샘플은 보장하기 위해 started 신호
        monitor_started.set()

        # 가능하면 peak 파일을 바로 쓰고, 없으면 current 샘플링 max로 peak를 만듦
        local_peak_bytes = 0

        while not stop_monitor.is_set():
            try:
                peak_bytes = read_cgroup_memory_peak_bytes(container_name)
                if peak_bytes is not None:
                    local_peak_bytes = max(local_peak_bytes, peak_bytes)
                else:
                    cur_bytes = read_cgroup_memory_current_bytes(container_name)
                    local_peak_bytes = max(local_peak_bytes, cur_bytes)

                peak_mem_kb = local_peak_bytes // 1024
            except Exception as e:
                # 조용히 묻지 말고 로그 남기자 (원인 파악용)
                logger.warning(f"[mem-monitor] read failed: {e}")

            time.sleep(0.02)  # 20ms

        # 종료 직전 한 번 더 찍어서 누락 방지
        try:
            peak_bytes = read_cgroup_memory_peak_bytes(container_name)
            if peak_bytes is not None:
                local_peak_bytes = max(local_peak_bytes, peak_bytes)
            else:
                cur_bytes = read_cgroup_memory_current_bytes(container_name)
                local_peak_bytes = max(local_peak_bytes, cur_bytes)
            peak_mem_kb = local_peak_bytes // 1024
        except:
            pass

    try:
        # 1) 코드 파일 생성
        main_path = os.path.join(tmp, "main.py")
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(wrapped_code)
        os.chmod(tmp, 0o755)
        os.chmod(main_path, 0o644)

        # 2) 컨테이너 create/start (sleep infinity로 유지)
        create_cmd = [
            "docker", "create",
            "--name", container_name,
            "--network", "none",
            "--cpus", str(cpu_limit),
            "--memory", f"{mem_mb}m",
            "--memory-swap", f"{mem_mb}m",
            "--pids-limit", "64",
            "--read-only",
            "--security-opt", "no-new-privileges",
            "--cap-drop", "ALL",
            "-v", f"{tmp}:/workspace:ro",
            "-w", "/workspace",
            PY_IMAGE,
            "sleep", "infinity"
        ]
        subprocess.run(create_cmd, check=True, capture_output=True, text=True)
        subprocess.run(["docker", "start", container_name], check=True, capture_output=True, text=True)

        # 3) 메모리 모니터 시작 (docker exec로 cgroup 파일 읽음)
        mon_thread = threading.Thread(target=monitor_memory, daemon=True)
        mon_thread.start()

        # monitor thread가 실제로 시작할 때까지 잠깐 대기 (샘플 0 방지)
        monitor_started.wait(timeout=0.2)

        # 4) 실제 실행은 docker exec로 수행
        exec_cmd = ["docker", "exec", "-i", container_name, "python", "-u", "main.py"]

        timeout_sec = max(0.1, time_limit_ms / 1000.0)
        p = subprocess.Popen(
            exec_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )

        stdout_buf = bytearray()
        stderr_buf = bytearray()
        stdout_over = False
        stderr_over = False
        killed = False
        kill_lock = threading.Lock()

        def kill_process():
            nonlocal killed
            with kill_lock:
                if not killed:
                    killed = True
                    try:
                        p.kill()
                    except:
                        pass
                    subprocess.run(["docker", "kill", container_name],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        def reader(stream, buf: bytearray, limit: int, mark: str):
            nonlocal stdout_over, stderr_over
            try:
                while True:
                    chunk = stream.read(READ_CHUNK_SIZE)
                    if not chunk:
                        break
                    remaining = limit - len(buf)
                    if remaining > 0:
                        buf.extend(chunk[:remaining])
                    if len(buf) >= limit:
                        if mark == "stdout":
                            stdout_over = True
                        else:
                            stderr_over = True
                        kill_process()
                        break
            except:
                pass

        t_out = threading.Thread(target=reader, args=(p.stdout, stdout_buf, MAX_STDOUT_SIZE, "stdout"))
        t_err = threading.Thread(target=reader, args=(p.stderr, stderr_buf, MAX_STDERR_SIZE, "stderr"))
        t_out.start()
        t_err.start()

        is_timeout = False
        try:
            if stdin:
                p.stdin.write(stdin.encode("utf-8"))
            p.stdin.close()
            p.wait(timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            is_timeout = True
            kill_process()

        t_out.join()
        t_err.join()

        # 5) 모니터 종료(여기서 peak_mem_kb 확정)
        stop_monitor.set()
        mon_thread.join(timeout=1.0)

        stdout_text = stdout_buf.decode(errors="replace")
        stderr_text = stderr_buf.decode(errors="replace")

        # python 내부 시간 파싱
        exec_time_ms = 0
        if "__CF_TIME__=" in stdout_text:
            parts = stdout_text.split("__CF_TIME__=")
            try:
                data = json.loads(parts[-1])
                exec_time_ms = int(data.get("time_ms", 0))
            except:
                pass
            stdout_text = parts[0].strip()

        # OOMKilled 확인
        is_oom = False
        try:
            oom_flag = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.OOMKilled}}", container_name],
                capture_output=True, text=True
            ).stdout.strip()
            if oom_flag.lower() == "true":
                is_oom = True
                stderr_text = "Memory Limit Exceeded"
        except:
            pass

        if is_timeout:
            stderr_text = "Time Limit Exceeded"
        elif stdout_over:
            stderr_text = "Output Limit Exceeded"
        elif stderr_over:
            stderr_text = "Error Output Limit Exceeded"

        # 여기서 peak_mem_kb는 최소 current라도 찍도록
        memory_usage_kb = peak_mem_kb

        return (
            stdout_text,
            stderr_text,
            exec_time_ms,
            memory_usage_kb,
            is_timeout,
            is_oom,
        )

    finally:
        subprocess.run(["docker", "rm", "-f", container_name],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.rmtree(tmp, ignore_errors=True)
