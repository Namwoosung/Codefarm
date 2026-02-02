import os
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Literal

import httpx
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from fastapi import Request
from utils.auth import verify_server_token

from models.model1 import run_model1
from models.model2 import run_model2
from utils.prompt_builder import build_prompt, sanitize_payload_for_model2, is_known_label, dedup_labels
from utils.prompt import build_gms_messages
from utils.json_utils import parse_json, has_banned

import inspect

print("[DEBUG] model1 path =", run_model1.__code__.co_filename)
print("[DEBUG] model1 is coroutine =", asyncio.iscoroutinefunction(run_model1))
print("[DEBUG] model1 source head =", inspect.getsource(run_model1)[:200])

load_dotenv()

REPORT_SERVER_TOKEN = os.getenv("REPORT_SERVER_TOKEN", "")
REQUIRE_SERVER_TOKEN = os.getenv("REQUIRE_SERVER_TOKEN", "0") == "1"

# =========================
# Env / Config
# =========================
GMS_API_KEY = os.getenv("GMS_API_KEY") or os.getenv("GMS_KEY")
if not GMS_API_KEY:
    raise RuntimeError("GMS_API_KEY (or GMS_KEY) is missing in .env")

GMS_CHAT_URL = os.getenv("GMS_CHAT_URL", "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions")
GMS_MODEL = os.getenv("GMS_MODEL", "gpt-5.2")
GMS_TIMEOUT = float(os.getenv("GMS_TIMEOUT", "30.0"))

# 동시요청 보호
QUEUE_MAXSIZE = int(os.getenv("INFER_QUEUE_MAXSIZE", "50"))
WORKERS = int(os.getenv("INFER_WORKERS", "2"))
ENQUEUE_TIMEOUT = float(os.getenv("ENQUEUE_TIMEOUT", "0.2"))
REQUEST_MAX_WAIT = float(os.getenv("REQUEST_MAX_WAIT", "30.0"))

MODEL1_TIMEOUT = float(os.getenv("MODEL1_TIMEOUT", "8.0"))
MODEL2_TIMEOUT = float(os.getenv("MODEL2_TIMEOUT", "8.0"))

app = FastAPI(title="Hint Server (M1->M2(prompt)->GMS) v6", version="6.0.0")

# =========================
# Request Schemas
# =========================
class UserInformation(BaseModel):
    age: int = Field(ge=6, le=18)
    coding_level: int = Field(ge=1, le=5)
    user_id: str

class ProblemInformation(BaseModel):
    algorithm: Optional[str] = None
    description: str
    difficulty: int = Field(ge=1, le=5)
    problem_id: str

class CodeSnapshot(BaseModel):
    timestamp: Optional[str] = None
    code: str

class PreviousJudgementItem(BaseModel):
    analysis: Optional[str] = None
    judged_at: str
    mistake_type: List[str] = Field(default_factory=list)

class HintRequest(BaseModel):
    started_at: str
    observed_at: str
    language: Literal["python"] = "python"
    user_information: UserInformation
    problem_information: ProblemInformation
    code_history: List[CodeSnapshot] = Field(default_factory=list)
    previous_judgement: List[PreviousJudgementItem] = Field(default_factory=list)
    # 있을 수도/없을 수도
    user_question: Optional[str] = None

# =========================
# Response Schemas (요구사항 고정)
# =========================
class CurrentJudgementOut(BaseModel):
    judged_at: str
    mistake_type: List[str]
    analysis: str = ""

class HintResponse(BaseModel):
    current_judgement: CurrentJudgementOut
    hint: Optional[str] = None  # ✅ null 허용

# =========================
# Queue + Session Lock
# =========================
@dataclass
class InferJob:
    session_id: str
    payload: Dict[str, Any]
    fut: "asyncio.Future[Dict[str, Any]]"

infer_queue: "asyncio.Queue[InferJob]" = asyncio.Queue(maxsize=QUEUE_MAXSIZE)

_session_locks: Dict[str, asyncio.Lock] = {}
_session_locks_guard = asyncio.Lock()

async def get_session_lock(session_id: str) -> asyncio.Lock:
    async with _session_locks_guard:
        lock = _session_locks.get(session_id)
        if lock is None:
            lock = asyncio.Lock()
            _session_locks[session_id] = lock
        return lock

# =========================
# GMS Call
# =========================
async def gms_chat(messages: List[Dict[str, str]], max_tokens: int = 700, temperature: float = 0.4) -> str:
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {GMS_API_KEY}"}
    body = {
        "model": GMS_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_completion_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=GMS_TIMEOUT) as client:
        r = await client.post(GMS_CHAT_URL, headers=headers, json=body)

    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"GMS error {r.status_code}: {r.text}")

    data = r.json()
    return data["choices"][0]["message"]["content"]

def now_iso() -> str:
    # UTC ISO8601 (예: 2026-01-31T01:23:45Z)
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

# =========================
# Build model2 input
# =========================
def build_model2_input(req_payload: Dict[str, Any], mistake_type: List[str]) -> Dict[str, Any]:
    # Drop any accidental meta fields coming from clients / older pipelines.
    model2_input = sanitize_payload_for_model2(req_payload)

    # user_question normalize: 없으면 ""
    model2_input["user_question"] = (model2_input.get("user_question") or "")

    # current_judgement는 model2 입력에서 요구한 형태(analysis 빈 문자열 포함)
    # Dedup + enforce No_Issue-only rule
    safe_labels = dedup_labels(mistake_type)
    model2_input["current_judgement"] = {"analysis": "", "mistake_type": safe_labels}

    # prompt 생성/주입
    # Prompt 생성/주입 (prompt-only; no meta fields)
    # Also do a light validation for unknown labels (log-only).
    unknown = [lb for lb in safe_labels if not is_known_label(lb)]
    if unknown:
        print(f"[WARN] Unknown labels from model1: {unknown}")

    model2_input["prompt"] = build_prompt(model2_input)

    return model2_input

# =========================
# Pipeline
# =========================
async def process_pipeline(req_payload: Dict[str, Any]) -> Dict[str, Any]:
    # 1) MODEL1
    try:
        m1 = await asyncio.wait_for(run_model1(req_payload), timeout=MODEL1_TIMEOUT)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="model1 timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"model1 failed: {e}")

    if not isinstance(m1, dict):
        raise HTTPException(status_code=500, detail="model1 output must be a dict")

    mistake_type = m1.get("mistake_type")
    if not isinstance(mistake_type, list) or not all(isinstance(x, str) for x in mistake_type):
        raise HTTPException(status_code=500, detail="model1 output must include mistake_type: List[str]")

    # 2) MODEL2 input (mistake_type + prompt 포함)
    model2_input = build_model2_input(req_payload, mistake_type)

    # 3) MODEL2 -> gms_input dict 생성
    try:
        gms_input = await asyncio.wait_for(run_model2(model2_input), timeout=MODEL2_TIMEOUT)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="model2 timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"model2 failed: {e}")

    if not isinstance(gms_input, dict):
        raise HTTPException(status_code=500, detail="model2 output must be a dict (gms_input)")

    # 4) GMS
    messages = build_gms_messages(gms_input)
    raw = await gms_chat(messages)

    # 5) parse + banned + repair 1회
    try:
        obj = parse_json(raw)
        if has_banned(obj):
            raise ValueError("banned terms")
    except Exception:
        repair_messages = messages + [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": "규칙을 어겼어. 금지 단어 없이, 아주 쉬운 말로, JSON만 다시 출력해줘."},
        ]
        raw2 = await gms_chat(repair_messages)
        obj = parse_json(raw2)
        if has_banned(obj):
            raise HTTPException(status_code=500, detail="Banned terms still present after repair.")

    # 6) hint 추출 (should_send=false면 hint=null)
    should_send = bool(obj.get("should_send", True))
    hint_content = (obj.get("hint_content") or "").strip()

    hint: Optional[str]
    if not should_send:
        hint = None
    else:
        hint = hint_content if hint_content else None  # 빈 문자열이면 null로 통일

    # 7) 최종 응답 스키마로 포장
    judged_at = now_iso()
    return {
        "current_judgement": {
            "judged_at": judged_at,
            "mistake_type": mistake_type,
            "analysis": "",
        },
        "hint": hint,
    }

# =========================
# Worker
# =========================
async def worker_loop(worker_id: int):
    while True:
        job = await infer_queue.get()
        try:
            lock = await get_session_lock(job.session_id)
            async with lock:
                result = await process_pipeline(job.payload)
            if not job.fut.done():
                job.fut.set_result(result)
        except Exception as e:
            if not job.fut.done():
                job.fut.set_exception(e)
        finally:
            infer_queue.task_done()

@app.on_event("startup")
async def startup():
    for i in range(WORKERS):
        asyncio.create_task(worker_loop(i))

from fastapi import Request
from utils.auth import verify_server_token

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    verify_server_token(request)  
    return await call_next(request)


# =========================
# Endpoint
# =========================
@app.post("/api/v1/sessions/{session_id}/hints/hint", response_model=HintResponse)
async def hint(session_id: str = Path(..., min_length=1), req: HintRequest = None):
    req_payload = req.model_dump()

    loop = asyncio.get_running_loop()
    fut: asyncio.Future = loop.create_future()
    job = InferJob(session_id=session_id, payload=req_payload, fut=fut)

    try:
        await asyncio.wait_for(infer_queue.put(job), timeout=ENQUEUE_TIMEOUT)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=429, detail="Too many requests (queue busy/full)")

    try:
        result = await asyncio.wait_for(fut, timeout=REQUEST_MAX_WAIT)
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out waiting in queue")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")
