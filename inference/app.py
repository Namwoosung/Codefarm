# app.py
import os
import json
import time
import uuid
import asyncio
import inspect
import logging
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from contextvars import ContextVar
from typing import Any, Dict, List, Optional, Literal

import httpx
from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from utils.auth import verify_server_token
from models.model1 import run_model1
from models.model2 import run_model2
from utils.prompt_builder import build_prompt, sanitize_payload_for_model2, is_known_label, dedup_labels
from utils.prompt import build_gms_messages
from utils.json_utils import parse_json, has_banned

# ============================================================
# Logging (request-scoped rid + JSON line logs)
# ============================================================

REQUEST_ID: ContextVar[str] = ContextVar("request_id", default="-")

def setup_logger() -> logging.Logger:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    return logging.getLogger("hint-server")

log = setup_logger()

def rid() -> str:
    return REQUEST_ID.get()

def log_event(event: str, **fields):
    base = {"event": event, "rid": rid()}
    base.update(fields)
    log.info(json.dumps(base, ensure_ascii=False))

def log_error(event: str, **fields):
    base = {"event": event, "rid": rid()}
    base.update(fields)
    log.error(json.dumps(base, ensure_ascii=False))


# ============================================================
# Load env
# ============================================================

load_dotenv("/srv/app/app/.env")

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

MODEL1_TIMEOUT = float(os.getenv("MODEL1_TIMEOUT", "15.0"))
MODEL2_TIMEOUT = float(os.getenv("MODEL2_TIMEOUT", "15.0"))

GMS_MAX_TOKENS = int(os.getenv("GMS_MAX_TOKENS", "700"))
GMS_TEMPERATURE = float(os.getenv("GMS_TEMPERATURE", "0.4"))


# ============================================================
# App
# ============================================================

app = FastAPI(title="Hint Server (M1->M2(prompt)->GMS) v7", version="7.0.0")


# ============================================================
# Request Schemas
# ============================================================

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
    user_question: Optional[str] = None

# =========================
# Response Schemas
# =========================
class CurrentJudgementOut(BaseModel):
    judged_at: str
    mistake_type: List[str]
    analysis: str = ""

class HintResponse(BaseModel):
    current_judgement: CurrentJudgementOut
    hint: Optional[str] = None  # null 허용


# ============================================================
# Queue + Session Lock
# ============================================================

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


# ============================================================
# Utils
# ============================================================

def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ============================================================
# Middleware: Trace first (rid + duration), then auth
# ============================================================

@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    _rid = request.headers.get("x-request-id") or str(uuid.uuid4())
    token = REQUEST_ID.set(_rid)
    t0 = time.perf_counter()
    try:
        response = await call_next(request)
        dt_ms = int((time.perf_counter() - t0) * 1000)
        response.headers["x-request-id"] = _rid
        log_event("http_done", path=str(request.url.path), status=response.status_code, ms=dt_ms)
        return response
    except Exception as e:
        dt_ms = int((time.perf_counter() - t0) * 1000)
        log_error(
            "http_fail",
            path=str(request.url.path),
            ms=dt_ms,
            err=str(e),
            tb=traceback.format_exc()[-1500:],
        )
        raise
    finally:
        REQUEST_ID.reset(token)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # verify_server_token 내부에서 REQUIRE_SERVER_TOKEN 등을 참고한다는 가정
    verify_server_token(request)
    return await call_next(request)


# ============================================================
# GMS Call
# ============================================================

async def gms_chat(messages: List[Dict[str, str]], max_tokens: int = GMS_MAX_TOKENS, temperature: float = GMS_TEMPERATURE) -> str:
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {GMS_API_KEY}"}
    body = {
        "model": GMS_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_completion_tokens": max_tokens,
    }

    t0 = time.perf_counter()
    async with httpx.AsyncClient(timeout=GMS_TIMEOUT) as client:
        r = await client.post(GMS_CHAT_URL, headers=headers, json=body)
    dt_ms = int((time.perf_counter() - t0) * 1000)

    if r.status_code != 200:
        log_error("gms_http_fail", status=r.status_code, ms=dt_ms, body_head=r.text[:600])
        raise HTTPException(status_code=502, detail=f"GMS error {r.status_code}: {r.text}")

    log_event("gms_http_ok", ms=dt_ms, status=r.status_code)

    data = r.json()
    return data["choices"][0]["message"]["content"]


# ============================================================
# Safe call wrapper (sync/async 혼재 대응)
# ============================================================

async def call_maybe_async(fn, *args, timeout: float, stage: str):
    t0 = time.perf_counter()
    try:
        if inspect.iscoroutinefunction(fn):
            out = await asyncio.wait_for(fn(*args), timeout=timeout)
        else:
            out = await asyncio.wait_for(run_in_threadpool(fn, *args), timeout=timeout)

        dt_ms = int((time.perf_counter() - t0) * 1000)
        log_event(f"{stage}_ok", ms=dt_ms, out_type=type(out).__name__)
        return out

    except asyncio.TimeoutError:
        dt_ms = int((time.perf_counter() - t0) * 1000)
        log_error(f"{stage}_timeout", ms=dt_ms, timeout=timeout)
        raise

    except Exception as e:
        dt_ms = int((time.perf_counter() - t0) * 1000)
        log_error(f"{stage}_fail", ms=dt_ms, err=str(e), tb=traceback.format_exc()[-1500:])
        raise


# ============================================================
# Build model2 input
# ============================================================

def build_model2_input(req_payload: Dict[str, Any], mistake_type: List[str]) -> Dict[str, Any]:
    model2_input = sanitize_payload_for_model2(req_payload)

    model2_input["user_question"] = (model2_input.get("user_question") or "")

    safe_labels = dedup_labels(mistake_type)
    model2_input["current_judgement"] = {"analysis": "", "mistake_type": safe_labels}

    unknown = [lb for lb in safe_labels if not is_known_label(lb)]
    if unknown:
        log_event("warn_unknown_labels", labels=unknown)

    model2_input["prompt"] = build_prompt(model2_input)
    return model2_input


# ============================================================
# Pipeline
# ============================================================

async def process_pipeline(req_payload: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    log_event("pipeline_start", session_id=session_id)

    # 1) MODEL1
    try:
        m1 = await call_maybe_async(run_model1, req_payload, timeout=MODEL1_TIMEOUT, stage="model1")
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="model1 timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"model1 failed: {e}")

    if not isinstance(m1, dict):
        log_error("model1_bad_type", got_type=type(m1).__name__)
        raise HTTPException(status_code=500, detail="model1 output must be a dict")

    mistake_type = m1.get("mistake_type")
    if not isinstance(mistake_type, list) or not all(isinstance(x, str) for x in mistake_type):
        log_error("model1_bad_mistake_type", mistake_type_repr=repr(mistake_type)[:500])
        raise HTTPException(status_code=500, detail="model1 output must include mistake_type: List[str]")

    log_event("model1_labels", labels=mistake_type, n=len(mistake_type))

    # 2) MODEL2 input (mistake_type + prompt 포함)
    model2_input = build_model2_input(req_payload, mistake_type)
    prompt_len = len(model2_input.get("prompt", "") or "")
    log_event("model2_input_built", prompt_len=prompt_len)

    # 3) MODEL2 -> gms_input dict 생성
    try:
        gms_input = await call_maybe_async(run_model2, model2_input, timeout=MODEL2_TIMEOUT, stage="model2")
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="model2 timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"model2 failed: {e}")

    if not isinstance(gms_input, dict):
        log_error("model2_bad_type", got_type=type(gms_input).__name__)
        raise HTTPException(status_code=500, detail="model2 output must be a dict (gms_input)")

    # ✅ model2 analysis 추출 (표준 키 후보)
    # analysis_out = ""
    # for k in ("analysis_pred", "model2_analysis", "analysis"):
    #     v = gms_input.get(k)
    #     if isinstance(v, str) and v.strip():
    #         analysis_out = v.strip()
    #         break
    # log_event("model2_analysis_len", n=len(analysis_out))
    
    analysis_out = (
        gms_input
        .get("current_judgement", {})
        .get("analysis", "")
    ).strip()

    log_event("model2_analysis_len", n=len(analysis_out))


    # 4) GMS
    messages = build_gms_messages(gms_input)
    log_event("gms_call", n_messages=len(messages))

    raw = await gms_chat(messages)
    log_event("gms_raw_len", n=len(raw or ""))

    # 5) parse + banned + repair 1회
    try:
        obj = parse_json(raw)
        if has_banned(obj):
            raise ValueError("banned terms")
        log_event("gms_parse_ok")
    except Exception as e:
        log_error("gms_parse_fail", err=str(e), raw_head=(raw or "")[:400])

        repair_messages = messages + [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": "규칙을 어겼어. 금지 단어 없이, 아주 쉬운 말로, JSON만 다시 출력해줘."},
        ]
        raw2 = await gms_chat(repair_messages)
        log_event("gms_repair_raw_len", n=len(raw2 or ""))

        obj = parse_json(raw2)
        if has_banned(obj):
            log_error("gms_banned_after_repair", obj_head=str(obj)[:400])
            raise HTTPException(status_code=500, detail="Banned terms still present after repair.")

        log_event("gms_repair_ok")

    # 6) hint 추출 (should_send=false면 hint=null)
    should_send = bool(obj.get("should_send", True))
    hint_content = (obj.get("hint_content") or "").strip()

    if not should_send:
        hint = None
        log_event("hint_suppressed", should_send=False)
    else:
        hint = hint_content if hint_content else None
        log_event("hint_ready", should_send=True, hint_len=(len(hint) if hint else 0))

    # 7) 최종 응답 (✅ analysis 포함)
    judged_at = now_iso()
    log_event("pipeline_done", session_id=session_id)

    return {
        "current_judgement": {
            "judged_at": judged_at,
            "mistake_type": mistake_type,
            "analysis": analysis_out,
        },
        "hint": hint,
    }


# ============================================================
# Worker
# ============================================================

async def worker_loop(worker_id: int):
    log_event("worker_start", worker_id=worker_id)
    while True:
        job = await infer_queue.get()
        try:
            lock = await get_session_lock(job.session_id)
            async with lock:
                log_event("job_start", worker_id=worker_id, session_id=job.session_id, qsize=infer_queue.qsize())
                result = await process_pipeline(job.payload, job.session_id)
                log_event("job_done", worker_id=worker_id, session_id=job.session_id)
            if not job.fut.done():
                job.fut.set_result(result)
        except Exception as e:
            log_error("job_fail", worker_id=worker_id, session_id=job.session_id, err=str(e))
            if not job.fut.done():
                job.fut.set_exception(e)
        finally:
            infer_queue.task_done()

@app.on_event("startup")
async def startup():
    log_event("startup", workers=WORKERS, queue_maxsize=QUEUE_MAXSIZE)
    for i in range(WORKERS):
        asyncio.create_task(worker_loop(i))


# ============================================================
# Endpoints
# ============================================================

@app.get("/health")
def health():
    return {
        "ok": True,
        "version": "7.0.0",
        "workers": WORKERS,
        "queue_maxsize": QUEUE_MAXSIZE,
    }

@app.post("/api/v1/sessions/{session_id}/hints/hint", response_model=HintResponse)
async def hint(session_id: str = Path(..., min_length=1), req: HintRequest = None):
    req_payload = req.model_dump()
    log_event("enqueue_try", session_id=session_id, qsize=infer_queue.qsize())

    loop = asyncio.get_running_loop()
    fut: asyncio.Future = loop.create_future()
    job = InferJob(session_id=session_id, payload=req_payload, fut=fut)

    try:
        await asyncio.wait_for(infer_queue.put(job), timeout=ENQUEUE_TIMEOUT)
        log_event("enqueue_ok", session_id=session_id, qsize=infer_queue.qsize())
    except asyncio.TimeoutError:
        log_error("enqueue_timeout", session_id=session_id, qsize=infer_queue.qsize())
        raise HTTPException(status_code=429, detail="Too many requests (queue busy/full)")

    try:
        result = await asyncio.wait_for(fut, timeout=REQUEST_MAX_WAIT)
        return result
    except asyncio.TimeoutError:
        log_error("request_wait_timeout", session_id=session_id, qsize=infer_queue.qsize())
        raise HTTPException(status_code=504, detail="Request timed out waiting in queue")
    except HTTPException:
        raise
    except Exception as e:
        log_error("pipeline_failed", session_id=session_id, err=str(e), tb=traceback.format_exc()[-1500:])
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")