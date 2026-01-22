import os, tempfile, time, subprocess, textwrap, uuid, shutil

PY_IMAGE = "codefarm-python:3.11"

def run_python_in_docker(code: str, stdin: str, time_limit_ms: int, mem_mb: int, cpu: float):
    # 호스트의 /tmp를 사용하여 임시 디렉토리 생성 (Docker 볼륨 마운트를 위해)
    # 컨테이너 내부에서 실행되므로 /tmp는 호스트와 공유되어야 함
    tmp_base = "/tmp"
    tmp = tempfile.mkdtemp(prefix="codefarm_", dir=tmp_base)
    try:
        main_path = os.path.join(tmp, "main.py")
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        # 절대 경로 사용 (Docker 볼륨 마운트를 위해)
        tmp_abs = os.path.abspath(tmp)

        container_name = f"codefarm-run-{uuid.uuid4().hex[:12]}"

        # docker run 옵션(보안/자원제한)
        cmd = [
            "docker", "run", "--rm", "-i",       # -i: stdin을 컨테이너로 전달
            "--name", container_name,
            "--network", "none",                 # 인터넷 차단
            "--cpus", str(cpu),                  # CPU 제한
            "--memory", f"{mem_mb}m",            # 메모리 제한
            "--pids-limit", "64",                # 프로세스 폭주 방지
            "--read-only",                       # 컨테이너 루트 FS 읽기 전용
            "--security-opt", "no-new-privileges",# 권한 상승 방지
            "-v", f"{tmp_abs}:/workspace:ro",    # 코드 마운트(읽기전용)
            "-w", "/workspace",
            PY_IMAGE,
            "python", "main.py"
        ]

        start = time.time()

        # timeout은 호스트에서 1차로 강제
        timeout_sec = max(0.1, time_limit_ms / 1000.0)

        try:
            p = subprocess.run(
                cmd,
                input=stdin,
                text=True,
                capture_output=True,
                timeout=timeout_sec
            )
            is_timeout = False
            stdout = p.stdout
            stderr = p.stderr
        except subprocess.TimeoutExpired:
            # timeout 발생 시 컨테이너 kill (혹시 남아있을 수 있으니)
            subprocess.run(["docker", "kill", container_name], capture_output=True, text=True)
            is_timeout = True
            stdout = ""
            stderr = "Time Limit Exceeded"

        exec_time_ms = int((time.time() - start) * 1000)
        return stdout, stderr, exec_time_ms, is_timeout
    finally:
        # 임시 디렉토리 정리
        try:
            shutil.rmtree(tmp)
        except:
            pass