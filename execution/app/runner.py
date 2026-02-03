import os
import tempfile
import time
import subprocess
import uuid
import shutil
import logging
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PY_IMAGE = "codefarm-python:3.11"
MAX_STDOUT_SIZE = 1 * 1024 * 1024  # 1MB


def read_cgroup_peak_memory(container_name: str) -> int:
    """
    컨테이너의 cgroup peak memory(KB) 반환
    v2: memory.peak
    v1: memory.max_usage_in_bytes
    """
    try:
        inspect = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Pid}}", container_name],
            capture_output=True,
            text=True,
        )
        pid = inspect.stdout.strip()
        if not pid.isdigit():
            return 0

        # cgroup v2
        peak_v2 = f"/proc/{pid}/root/sys/fs/cgroup/memory.peak"
        if os.path.exists(peak_v2):
            with open(peak_v2, "r") as f:
                return int(f.read().strip()) // 1024

        # cgroup v1
        peak_v1 = f"/proc/{pid}/root/sys/fs/cgroup/memory/memory.max_usage_in_bytes"
        if os.path.exists(peak_v1):
            with open(peak_v1, "r") as f:
                return int(f.read().strip()) // 1024

    except Exception as e:
        logger.warning(f"Peak memory read failed: {e}")

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

    try:
        # 코드 파일 생성
        main_path = os.path.join(tmp, "main.py")
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(code)

        os.chmod(tmp, 0o755)
        os.chmod(main_path, 0o644)

        # docker run
        cmd = [
            "docker", "run", "-i",
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
            "python", "-u", "main.py"
        ]

        start_time = time.perf_counter()
        timeout_sec = max(0.1, time_limit_ms / 1000.0)

        p = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
        )

        stdout_chunks = []
        total_stdout_size = 0
        killed_for_stdout = False

        # stdout 제한 처리
        def read_stdout():
            nonlocal total_stdout_size, killed_for_stdout
            for line in p.stdout:
                total_stdout_size += len(line.encode("utf-8"))
                if total_stdout_size > MAX_STDOUT_SIZE:
                    killed_for_stdout = True
                    p.kill()
                    break
                stdout_chunks.append(line)

        stdout_thread = threading.Thread(target=read_stdout)
        stdout_thread.start()

        # stdin 전달 + timeout 처리
        try:
            if stdin:
                p.stdin.write(stdin)
            p.stdin.close()
            p.wait(timeout=timeout_sec)
            is_timeout = False
        except subprocess.TimeoutExpired:
            p.kill()
            is_timeout = True

        stdout_thread.join()

        exec_time_ms = int((time.perf_counter() - start_time) * 1000)

        stderr_output = p.stderr.read()
        stdout_output = "".join(stdout_chunks)

        is_oom = False
        if p.returncode == 137:
            is_oom = True
            stderr_output = "Memory Limit Exceeded"

        if killed_for_stdout:
            stderr_output = "Output Limit Exceeded"

        if is_timeout:
            stderr_output = "Time Limit Exceeded"

        # 컨테이너가 살아있는 동안 peak memory 읽기
        memory_usage = read_cgroup_peak_memory(container_name)

        return (
            stdout_output,
            stderr_output,
            exec_time_ms,
            memory_usage,
            is_timeout,
            is_oom,
        )

    finally:
        # 컨테이너 삭제
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        shutil.rmtree(tmp, ignore_errors=True)
