import os
import tempfile
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


def _docker_exec_read_int(container_name: str, path: str, timeout: float = 0.2) -> int | None:
    """
    컨테이너 내부 파일을 docker exec cat으로 읽어 정수로 파싱.
    실패 시 None.
    """
    try:
        r = subprocess.run(
            ["docker", "exec", container_name, "cat", path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if r.returncode != 0:
            return None

        s = r.stdout.strip()
        if not s or s == "max":
            return None

        return int(s)
    except Exception:
        return None


def read_cgroup_peak_or_current_kb(container_name: str) -> int:
    """
    v2: memory.peak 우선, 없으면 memory.current
    v1: memory.max_usage_in_bytes 우선, 없으면 memory.usage_in_bytes
    """
    # cgroup v2
    peak_v2 = _docker_exec_read_int(container_name, "/sys/fs/cgroup/memory.peak")
    if peak_v2 is not None:
        return peak_v2 // 1024

    cur_v2 = _docker_exec_read_int(container_name, "/sys/fs/cgroup/memory.current")
    if cur_v2 is not None:
        return cur_v2 // 1024

    # cgroup v1
    peak_v1 = _docker_exec_read_int(container_name, "/sys/fs/cgroup/memory/memory.max_usage_in_bytes")
    if peak_v1 is not None:
        return peak_v1 // 1024

    cur_v1 = _docker_exec_read_int(container_name, "/sys/fs/cgroup/memory/memory.usage_in_bytes")
    if cur_v1 is not None:
        return cur_v1 // 1024

    return 0


def run_python_in_docker(
    code: str,
    stdin: str,
    time_limit_ms: int,
    mem_mb: int,
    cpu_limit: float,
):
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

    peak_mem_kb = 0  # "kill 전에 한번 읽고" 보존하기 위한 변수

    def snapshot_memory():
        """컨테이너가 살아있을 때만 읽을 수 있으니, 필요할 때 한번 찍어두기"""
        nonlocal peak_mem_kb
        try:
            kb = read_cgroup_peak_or_current_kb(container_name)
            if kb > peak_mem_kb:
                peak_mem_kb = kb
        except Exception:
            pass

    try:
        # 1) 코드 파일 생성
        main_path = os.path.join(tmp, "main.py")
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(wrapped_code)

        os.chmod(tmp, 0o755)
        os.chmod(main_path, 0o644)

        # 2) 컨테이너 create/start (sleep infinity)
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
        subprocess.run(create_cmd, check=True)
        subprocess.run(["docker", "start", container_name], check=True)

        # 3) python 실행 (docker exec)
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

        def kill_process_and_container():
            nonlocal killed
            with kill_lock:
                if killed:
                    return
                killed = True

                snapshot_memory()

                try:
                    p.kill()
                except:
                    pass

                # 컨테이너 내부 python이 남아있을 수 있으므로 컨테이너 kill
                subprocess.run(
                    ["docker", "kill", container_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

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
                        kill_process_and_container()
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
            kill_process_and_container()

        t_out.join()
        t_err.join()

        # 정상 종료 케이스에서도 마지막에 한번 더 읽어서 확정
        snapshot_memory()

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
                capture_output=True,
                text=True,
                timeout=0.3,
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

        return (
            stdout_text,
            stderr_text,
            exec_time_ms,
            peak_mem_kb,
            is_timeout,
            is_oom,
        )

    finally:
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        shutil.rmtree(tmp, ignore_errors=True)
