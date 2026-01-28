import os, tempfile, time, subprocess, textwrap, uuid, shutil
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PY_IMAGE = "codefarm-python:3.11"

def run_python_in_docker(code: str, stdin: str, time_limit_ms: int, mem_mb: int, cpu: float):
    # 호스트의 /tmp를 사용하여 임시 디렉토리 생성 (Docker 볼륨 마운트를 위해)
    # Docker-in-Docker 환경에서는 호스트의 /tmp가 마운트되어 있어야 함
    tmp_base = "/tmp"
    tmp = tempfile.mkdtemp(prefix="codefarm_", dir=tmp_base)
    try:
        main_path = os.path.join(tmp, "main.py")
        
        # 사용자가 solution() 함수만 정의하고 호출하지 않는 경우를 대비해
        # 실행 코드를 추가해줌
        submission_code = code + textwrap.dedent("""
        
        # --- Auto-generated execution logic ---
        if __name__ == "__main__":
            if "solution" in globals() and callable(globals()["solution"]):
                try:
                    solution()
                except Exception as e:
                    import traceback
                    traceback.print_exc()
        """)

        with open(main_path, "w", encoding="utf-8") as f:
            f.write(submission_code)

        os.chmod(tmp, 0o755)
        os.chmod(main_path, 0o644)
        
        # Docker-in-Docker: 호스트 관점의 절대 경로 사용
        # 실행 컨테이너의 /tmp가 호스트의 /tmp와 마운트되어 있으므로
        # 여기서 생성한 경로를 그대로 사용
        tmp_abs = tmp  # 이미 /tmp/codefarm_xxx 형태

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
            "python", "-u", "main.py"            # -u: Unbuffered output
        ]

        logger.info(f"Executing Docker command: {' '.join(cmd)}")
        logger.info(f"Code to execute:\n{code}")
        logger.info(f"Stdin: {stdin}")

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
            
            logger.info(f"Docker execution completed. Return code: {p.returncode}")
            logger.info(f"Stdout length: {len(stdout)}, Stderr length: {len(stderr)}")
            if stdout:
                logger.info(f"Stdout: {stdout}")
            else:
                logger.warning("Stdout is empty!")
            if stderr:
                logger.warning(f"Stderr: {stderr}")
            else:
                logger.info("Stderr is empty (no errors)")
                
        except subprocess.TimeoutExpired:
            # timeout 발생 시 컨테이너 kill (혹시 남아있을 수 있으니)
            subprocess.run(["docker", "kill", container_name], capture_output=True, text=True)
            is_timeout = True
            stdout = ""
            stderr = "Time Limit Exceeded"
            logger.warning(f"Execution timed out after {timeout_sec}s")

        exec_time_ms = int((time.time() - start) * 1000)
        logger.info(f"Total execution time: {exec_time_ms}ms")
        return stdout, stderr, exec_time_ms, is_timeout
    finally:
        # 임시 디렉토리 정리
        try:
            shutil.rmtree(tmp)
        except:
            pass