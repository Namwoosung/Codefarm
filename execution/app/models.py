from pydantic import BaseModel, Field
from typing import Literal, Optional

# 지원 언어 타입 (확장 대비)
Language = Literal["PYTHON"]


class ExecuteRequest(BaseModel):
    language: Language

    code: str = Field(
        ...,
        max_length=200_000,
        description="User source code (max 200KB)"
    )

    stdin: Optional[str] = Field(
        default="",
        max_length=100_000,
        description="Standard input (max 100KB)"
    )

    timeLimitMs: int = Field(
        ...,
        gt=0,
        le=10_000,
        description="Execution time limit in milliseconds"
    )

    memoryLimitMb: int = Field(
        ...,
        gt=16,
        le=1024,
        description="Memory limit in MB"
    )

    cpuLimit: float = Field(
        ...,
        gt=0.0,
        le=2.0,
        description="CPU core limit (e.g., 0.5)"
    )


class ExecuteResult(BaseModel):
    stdout: str
    stderr: str
    execTime: int        # ms (python process wall time)
    memoryUsage: int     # KB (cgroup peak)
    isTimeout: bool
    isOom: bool
