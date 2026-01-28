from fastapi import FastAPI, HTTPException
from app.models import ExecuteRequest, ExecuteResult
from app.runner import run_python_in_docker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/execute", response_model=ExecuteResult)
def execute(req: ExecuteRequest):
    logger.info(f"Received execution request: language={req.language}, code_length={len(req.code)}")
    
    if req.language != "PYTHON":
        raise HTTPException(status_code=400, detail="Unsupported language")

    stdout, stderr, exec_time, memory_usage, is_timeout = run_python_in_docker(
        code=req.code,
        stdin=req.stdin,
        time_limit_ms=req.timeLimitMs,
        mem_mb=req.memoryLimitMb,
        cpu=req.cpuLimit,
    )

    result = ExecuteResult(
        stdout=stdout,
        stderr=stderr,
        execTime=exec_time,
        memoryUsage=memory_usage,
        isTimeout=is_timeout,
    )
    
    logger.info(f"Returning result: stdout_len={len(stdout)}, stderr_len={len(stderr)}, execTime={exec_time}ms, isTimeout={is_timeout}")
    
    return result
