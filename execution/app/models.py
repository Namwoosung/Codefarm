from pydantic import BaseModel, Field
from typing import Literal, Optional

Language = Literal["PYTHON"]

class ExecuteRequest(BaseModel):
    language: Language
    code: str
    stdin: str = ""
    timeLimitMs: int = Field(default=2000)
    memoryLimitMb: int = Field(default=128)
    cpuLimit: float = Field(default=0.5, ge=0.1, le=2.0)

class ExecuteResult(BaseModel):
    stdout: str
    stderr: str
    execTime: int          # ms
    memoryUsage: int       # KB
    isTimeout: bool
    isOom: bool
