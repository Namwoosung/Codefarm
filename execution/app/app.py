from fastapi import FastAPI, HTTPException
from app.models import ExecuteRequest, ExecuteResult
from app.runner import run_python_in_docker
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CodeFarm Execution Server",
    version="1.0.0"
)

MAX_CONCURRENT_EXECUTIONS = 4
SUPPORTED_LANGUAGES = {"PYTHON"}

semaphore = asyncio.Semaphore(MAX_CONCURRENT_EXECUTIONS)


@app.post("/execute", response_model=ExecuteResult)
async def execute(req: ExecuteRequest):

    # 언어 검증 (Literal이 있지만 방어 차원에서 한 번 더)
    if req.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Unsupported language")

    logger.info(
        f"[REQUEST] "
        f"lang={req.language} "
        f"code_len={len(req.code)} "
        f"stdin_len={len(req.stdin or '')}"
    )

    try:
        # 동시 실행 제한 + thread offloading
        async with semaphore:
            stdout, stderr, exec_time, memory_usage, is_timeout, is_oom = \
                await asyncio.to_thread(
                    run_python_in_docker,
                    req.code,
                    req.stdin or "",
                    req.timeLimitMs,
                    req.memoryLimitMb,
                    req.cpuLimit,
                )

    except Exception as e:
        logger.exception("[EXECUTION ERROR]")
        raise HTTPException(
            status_code=500,
            detail="Execution Server Internal Error",
        )

    logger.info(
        f"[RESULT] "
        f"time={exec_time}ms "
        f"mem={memory_usage}KB "
        f"timeout={is_timeout} "
        f"oom={is_oom} "
        f"stdout_len={len(stdout)} "
        f"stderr_len={len(stderr)}"
    )

    return ExecuteResult(
        stdout=stdout,
        stderr=stderr,
        execTime=exec_time,
        memoryUsage=memory_usage,
        isTimeout=is_timeout,
        isOom=is_oom,
    )
