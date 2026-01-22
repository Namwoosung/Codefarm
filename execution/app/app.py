from fastapi import FastAPI, HTTPException
from app.models import ExecuteRequest, ExecuteResult
from app.runner import run_python_in_docker

app = FastAPI()

@app.post("/execute", response_model=ExecuteResult)
def execute(req: ExecuteRequest):
    if req.language != "PYTHON":
        raise HTTPException(status_code=400, detail="Unsupported language")

    stdout, stderr, exec_time, is_timeout = run_python_in_docker(
        code=req.code,
        stdin=req.stdin,
        time_limit_ms=req.timeLimitMs,
        mem_mb=req.memoryLimitMb,
        cpu=req.cpuLimit,
    )

    return ExecuteResult(
        stdout=stdout,
        stderr=stderr,
        execTime=exec_time,
        isTimeout=is_timeout,
    )
