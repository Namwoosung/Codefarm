# app.py (pipeline split: infer_queue + gms_queue)  -- p95/p99 stabilized
import os
import re
import json
import time
import uuid
import asyncio
import inspect
import logging
import traceback
import hashlib
from collections import deque
from difflib import SequenceMatcher
from dataclasses import dataclass
from datetime import datetime, timezone
from contextvars import ContextVar
from typing import Any, Dict, List, Optional, Literal

import httpx
from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from dotenv import find_dotenv, load_dotenv

from utils.auth import verify_server_token
from models.model1 import run_model1
from models.model2 import run_model2
from utils.prompt_builder import (
    build_prompt,
    sanitize_payload_for_model2,
    is_known_label,
    dedup_labels,
)
from utils.prompt import build_gms_messages
from utils.json_utils import parse_json, has_banned_text  # ✅ A안: hint_content만 금지어 검사


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
# NOTE: Windows 로컬에서도 동작하게 find_dotenv 우선
load_dotenv(find_dotenv("./srv/app/app/.env"))

REPORT_SERVER_TOKEN = os.getenv("REPORT_SERVER_TOKEN", "")
REQUIRE_SERVER_TOKEN = os.getenv("REQUIRE_SERVER_TOKEN", "0") == "1"

# =========================
# Env / Config
# =========================
GMS_API_KEY = os.getenv("GMS_API_KEY") or os.getenv("GMS_KEY")
if not GMS_API_KEY:
    raise RuntimeError("GMS_API_KEY (or GMS_KEY) is missing in .env")

GMS_CHAT_URL = os.getenv(
    "GMS_CHAT_URL",
    "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions",
)
GMS_MODEL = os.getenv("GMS_MODEL", "gpt-4o-mini")
GMS_TIMEOUT = float(os.getenv("GMS_TIMEOUT", "30.0"))

# 동시요청 보호(Queue)
QUEUE_MAXSIZE = int(os.getenv("INFER_QUEUE_MAXSIZE", "50"))
WORKERS = int(os.getenv("INFER_WORKERS", "2"))
ENQUEUE_TIMEOUT = float(os.getenv("ENQUEUE_TIMEOUT", "0.2"))
REQUEST_MAX_WAIT = float(os.getenv("REQUEST_MAX_WAIT", "30.0"))

# ✅ GMS stage 분리 후: 별도 워커/큐 설정
GMS_QUEUE_MAXSIZE = int(os.getenv("GMS_QUEUE_MAXSIZE", str(QUEUE_MAXSIZE)))
GMS_WORKERS = int(os.getenv("GMS_WORKERS", "8"))
GMS_ENQUEUE_TIMEOUT = float(os.getenv("GMS_ENQUEUE_TIMEOUT", "0.2"))

MODEL1_TIMEOUT = float(os.getenv("MODEL1_TIMEOUT", "20.0"))
MODEL2_TIMEOUT = float(os.getenv("MODEL2_TIMEOUT", "20.0"))

GMS_MAX_TOKENS = int(os.getenv("GMS_MAX_TOKENS", "700"))
GMS_TEMPERATURE = float(os.getenv("GMS_TEMPERATURE", "0.4"))

# ============================================================
# p95/p99 Stabilizers (IMPORTANT)
# ============================================================
GPU_CONCURRENCY = int(os.getenv("GPU_CONCURRENCY", "2"))
MODEL2_CONCURRENCY = int(os.getenv("MODEL2_CONCURRENCY", "2"))
GMS_CONCURRENCY = int(os.getenv("GMS_CONCURRENCY", str(GMS_WORKERS)))

_gpu_sem = asyncio.Semaphore(max(1, GPU_CONCURRENCY))
_model2_sem = asyncio.Semaphore(max(1, MODEL2_CONCURRENCY))
_gms_sem = asyncio.Semaphore(max(1, GMS_CONCURRENCY))


# ============================================================
# App
# ============================================================

app = FastAPI(
    title="Hint Server (M1->M2(prompt)->GMS) v8-pipeline+p95p99",
    version="8.1.0",
)


# ============================================================
# Request Schemas
# ============================================================

class UserInformation(BaseModel):
    age: int = Field(ge=1, le=200)
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
    hint: Optional[str] = None


class HintRequest(BaseModel):
    started_at: str
    observed_at: str
    language: Literal["python"] = "python"
    user_information: UserInformation
    problem_information: ProblemInformation
    code_history: List[CodeSnapshot] = Field(default_factory=list)
    previous_judgement: List[PreviousJudgementItem] = Field(default_factory=list)
    user_question: Optional[str] = None


# ============================================================
# Response Schemas
# ============================================================

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


@dataclass
class GmsJob:
    session_id: str
    payload: Dict[str, Any]                # 원본 req payload(로그/확장 대비)
    gms_input: Dict[str, Any]              # model2 output dict (gms_input)
    mistake_type: List[str]                # model1 labels
    analysis_out: str                      # model2 analysis
    fut: "asyncio.Future[Dict[str, Any]]"  # 최종 응답 future


infer_queue: "asyncio.Queue[InferJob]" = asyncio.Queue(maxsize=QUEUE_MAXSIZE)
gms_queue: "asyncio.Queue[GmsJob]" = asyncio.Queue(maxsize=GMS_QUEUE_MAXSIZE)

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
# Hint Dedup (Hard guard using previous_judgement + session cache)
# ============================================================

HINT_DEDUP_WINDOW_SEC = float(os.getenv("HINT_DEDUP_WINDOW_SEC", "900"))  # 15m
HINT_DEDUP_MAX_PER_SESSION = int(os.getenv("HINT_DEDUP_MAX_PER_SESSION", "20"))
HINT_NEAR_DUP_RATIO = float(os.getenv("HINT_NEAR_DUP_RATIO", "0.92"))  # near-dup threshold

_recent_hint_hashes: Dict[str, deque] = {}  # session_id -> deque[(ts, hash)]
_recent_hint_guard = asyncio.Lock()

_ws_re = re.compile(r"\s+")
_punct_re = re.compile(r"[^\w가-힣]+")


def _normalize_hint(s: str) -> str:
    s = (s or "").strip().lower()
    s = _ws_re.sub(" ", s)
    s = _punct_re.sub("", s)
    s = _ws_re.sub(" ", s).strip()
    return s


def _hint_hash(norm: str) -> str:
    return hashlib.sha256((norm or "").encode("utf-8")).hexdigest()


def _extract_prev_hints(req_payload: Dict[str, Any]) -> List[str]:
    prev = req_payload.get("previous_judgement") or []
    out: List[str] = []
    if isinstance(prev, list):
        for it in prev:
            if isinstance(it, dict):
                h = it.get("hint")
                if isinstance(h, str) and h.strip():
                    out.append(h.strip())
    return out


def _is_near_duplicate(a_norm: str, b_norm: str) -> bool:
    if not a_norm or not b_norm:
        return False
    if a_norm == b_norm:
        return True
    la, lb = len(a_norm), len(b_norm)
    if min(la, lb) == 0:
        return False
    if max(la, lb) / max(1, min(la, lb)) > 1.6:
        return False
    ratio = SequenceMatcher(None, a_norm, b_norm).ratio()
    return ratio >= HINT_NEAR_DUP_RATIO


async def _seen_in_session_cache(session_id: str, hint_hash: str) -> bool:
    now = time.time()
    async with _recent_hint_guard:
        dq = _recent_hint_hashes.get(session_id)
        if dq is None:
            dq = deque()
            _recent_hint_hashes[session_id] = dq

        while dq and (now - dq[0][0]) > HINT_DEDUP_WINDOW_SEC:
            dq.popleft()

        if any(prev_h == hint_hash for _, prev_h in dq):
            return True

        dq.append((now, hint_hash))
        while len(dq) > HINT_DEDUP_MAX_PER_SESSION:
            dq.popleft()

        return False


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
    verify_server_token(request)
    return await call_next(request)


# ============================================================
# HTTP client (reused)
# - Windows에서 http2=True 사용 시 h2 미설치로 ImportError 발생 가능
# - 설치되어 있으면 http2, 아니면 http1.1로 fallback
# ============================================================

def _build_http_client() -> httpx.AsyncClient:
    limits = httpx.Limits(max_connections=200, max_keepalive_connections=50)
    timeout = httpx.Timeout(GMS_TIMEOUT, connect=min(10.0, GMS_TIMEOUT))

    http2_enabled = False
    try:
        import h2  # noqa: F401
        http2_enabled = True
    except Exception:
        http2_enabled = False

    log_event("http_client_build", http2=http2_enabled)
    return httpx.AsyncClient(timeout=timeout, limits=limits, http2=http2_enabled)


# ============================================================
# GMS Call (client reused) + concurrency cap
# ============================================================

async def gms_chat(
    messages: List[Dict[str, str]],
    max_tokens: int = GMS_MAX_TOKENS,
    temperature: float = GMS_TEMPERATURE,
) -> str:
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {GMS_API_KEY}"}
    body = {
        "model": GMS_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_completion_tokens": max_tokens,
    }

    async with _gms_sem:
        t0 = time.perf_counter()
        client: httpx.AsyncClient = app.state.http
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
# Stage 1: MODEL pipeline (MODEL1 -> MODEL2) only
# ============================================================

async def process_models(req_payload: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    log_event("pipeline_model_start", session_id=session_id)

    async with _gpu_sem:
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

        model2_input = build_model2_input(req_payload, mistake_type)
        prompt_len = len(model2_input.get("prompt", "") or "")
        log_event("model2_input_built", prompt_len=prompt_len)

        async with _model2_sem:
            try:
                gms_input = await call_maybe_async(run_model2, model2_input, timeout=MODEL2_TIMEOUT, stage="model2")
            except asyncio.TimeoutError:
                raise HTTPException(status_code=504, detail="model2 timeout")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"model2 failed: {e}")

    if not isinstance(gms_input, dict):
        log_error("model2_bad_type", got_type=type(gms_input).__name__)
        raise HTTPException(status_code=500, detail="model2 output must be a dict (gms_input)")

    analysis_out = (gms_input.get("current_judgement", {}) or {}).get("analysis", "")
    analysis_out = (analysis_out or "").strip()
    log_event("model2_analysis_len", n=len(analysis_out))

    log_event("pipeline_model_done", session_id=session_id)

    return {
        "mistake_type": mistake_type,
        "analysis_out": analysis_out,
        "gms_input": gms_input,
    }


# ============================================================
# Stage 2: GMS pipeline (GMS call + parse/repair + final response)
# ============================================================

async def process_gms_stage(job: GmsJob) -> Dict[str, Any]:
    session_id = job.session_id
    log_event("pipeline_gms_start", session_id=session_id)

    pi = (job.gms_input.get("problem_information") or {})
    log_event(
        "gms_prompt_mode",
        session_id=session_id,
        problem_id=str(pi.get("problem_id") or ""),
    )

    messages = build_gms_messages(job.gms_input)
    log_event("gms_call", n_messages=len(messages))

    raw = await gms_chat(messages)
    log_event("gms_raw_len", n=len(raw or ""))

    try:
        obj = parse_json(raw)

        # ✅ A안(추천): 금지어 검사를 "hint_content"만 검사
        hint_text = obj.get("hint_content", None)
        if isinstance(hint_text, str) and hint_text.strip():
            if has_banned_text(hint_text):
                raise ValueError("banned terms in hint_content")

        log_event("gms_parse_ok")
    except Exception as e:
        log_error("gms_parse_fail", err=str(e), raw_head=(raw or "")[:400])

        repair_messages = messages + [
            {"role": "assistant", "content": raw},
            {
                "role": "user",
                "content": "규칙을 어겼어. 금지 단어 없이, 아주 쉬운 말로, JSON 하나만 다시 출력해줘.",
            },
        ]
        raw2 = await gms_chat(repair_messages)
        log_event("gms_repair_raw_len", n=len(raw2 or ""))

        obj = parse_json(raw2)

        # ✅ A안(추천): repair 후에도 hint_content만 검사
        hint_text2 = obj.get("hint_content", None)
        if isinstance(hint_text2, str) and hint_text2.strip():
            if has_banned_text(hint_text2):
                log_error("gms_banned_after_repair", obj_head=str(obj)[:400])
                raise HTTPException(
                    status_code=500,
                    detail="Banned terms still present after repair (hint_content).",
                )

        log_event("gms_repair_ok")

    should_send = bool(obj.get("should_send", True))

    hint_content_val = obj.get("hint_content", None)
    hint_content = ""
    if isinstance(hint_content_val, str):
        hint_content = hint_content_val.strip()

    if not should_send:
        hint = None
        log_event("hint_suppressed", should_send=False)
    else:
        hint = hint_content if hint_content else None
        log_event("hint_ready", should_send=True, hint_len=(len(hint) if hint else 0))

    # ✅ Hard Dedup (previous_judgement + session cache)
    if hint is not None:
        prev_hints = _extract_prev_hints(job.payload)
        hint_norm = _normalize_hint(hint)
        h_hash = _hint_hash(hint_norm)

        duplicated_by_prev = False
        for ph in prev_hints:
            ph_norm = _normalize_hint(ph)
            if not ph_norm:
                continue
            if ph_norm == hint_norm or _is_near_duplicate(hint_norm, ph_norm):
                duplicated_by_prev = True
                break

        if duplicated_by_prev:
            log_event(
                "hint_dedup_suppressed",
                reason="previous_judgement",
                prev_n=len(prev_hints),
                hint_len=len(hint),
            )
            hint = None
        else:
            log_event("hint_dedup_checked", prev_n=len(prev_hints), hint_norm_len=len(hint_norm))

        if hint is not None:
            seen = await _seen_in_session_cache(session_id, h_hash)
            if seen:
                log_event("hint_dedup_suppressed", reason="session_cache", hint_len=len(hint))
                hint = None

    judged_at = now_iso()
    log_event("pipeline_gms_done", session_id=session_id)

    return {
        "current_judgement": {
            "judged_at": judged_at,
            "mistake_type": job.mistake_type,
            "analysis": job.analysis_out,
        },
        "hint": hint,
    }


# ============================================================
# Workers
# ============================================================

async def infer_worker_loop(worker_id: int):
    log_event("worker_start", worker_id=worker_id, stage="infer")
    while True:
        job = await infer_queue.get()
        try:
            lock = await get_session_lock(job.session_id)
            async with lock:
                log_event(
                    "job_start",
                    worker_id=worker_id,
                    session_id=job.session_id,
                    stage="infer",
                    qsize=infer_queue.qsize(),
                )
                m = await process_models(job.payload, job.session_id)
                log_event("job_done", worker_id=worker_id, session_id=job.session_id, stage="infer")

            gjob = GmsJob(
                session_id=job.session_id,
                payload=job.payload,
                gms_input=m["gms_input"],
                mistake_type=m["mistake_type"],
                analysis_out=m["analysis_out"],
                fut=job.fut,
            )

            try:
                await asyncio.wait_for(gms_queue.put(gjob), timeout=GMS_ENQUEUE_TIMEOUT)
                log_event("enqueue_gms_ok", session_id=job.session_id, qsize=gms_queue.qsize())
            except asyncio.TimeoutError:
                log_error("enqueue_gms_timeout", session_id=job.session_id, qsize=gms_queue.qsize())
                if not job.fut.done():
                    job.fut.set_exception(
                        HTTPException(status_code=429, detail="Too many requests (gms queue busy/full)")
                    )
            except Exception as e:
                log_error("enqueue_gms_fail", session_id=job.session_id, err=str(e))
                if not job.fut.done():
                    job.fut.set_exception(
                        HTTPException(status_code=500, detail=f"Failed to enqueue gms job: {e}")
                    )

        except HTTPException as he:
            log_error(
                "job_fail",
                worker_id=worker_id,
                session_id=job.session_id,
                stage="infer",
                err=str(he.detail),
            )
            if not job.fut.done():
                job.fut.set_exception(he)
        except Exception as e:
            log_error("job_fail", worker_id=worker_id, session_id=job.session_id, stage="infer", err=str(e))
            if not job.fut.done():
                job.fut.set_exception(e)
        finally:
            infer_queue.task_done()


async def gms_worker_loop(worker_id: int):
    log_event("worker_start", worker_id=worker_id, stage="gms")
    while True:
        job = await gms_queue.get()
        try:
            result = await process_gms_stage(job)
            if not job.fut.done():
                job.fut.set_result(result)

        except HTTPException as he:
            log_error(
                "job_fail",
                worker_id=worker_id,
                session_id=job.session_id,
                stage="gms",
                err=str(he.detail),
            )
            if not job.fut.done():
                job.fut.set_exception(he)
        except Exception as e:
            log_error("job_fail", worker_id=worker_id, session_id=job.session_id, stage="gms", err=str(e))
            if not job.fut.done():
                job.fut.set_exception(e)
        finally:
            gms_queue.task_done()


# ============================================================
# Startup / Shutdown
# ============================================================

@app.on_event("startup")
async def startup():
    log_event(
        "startup",
        version=app.version,
        infer_workers=WORKERS,
        gms_workers=GMS_WORKERS,
        infer_queue_maxsize=QUEUE_MAXSIZE,
        gms_queue_maxsize=GMS_QUEUE_MAXSIZE,
        gpu_concurrency=GPU_CONCURRENCY,
        model2_concurrency=MODEL2_CONCURRENCY,
        gms_concurrency=GMS_CONCURRENCY,
        hint_dedup_window_sec=HINT_DEDUP_WINDOW_SEC,
        hint_near_dup_ratio=HINT_NEAR_DUP_RATIO,
        hint_dedup_max_per_session=HINT_DEDUP_MAX_PER_SESSION,
    )

    app.state.http = _build_http_client()

    for i in range(WORKERS):
        asyncio.create_task(infer_worker_loop(i))
    for i in range(GMS_WORKERS):
        asyncio.create_task(gms_worker_loop(i))


@app.on_event("shutdown")
async def shutdown():
    client = getattr(app.state, "http", None)
    if client:
        await client.aclose()
    log_event("shutdown")


# ============================================================
# Endpoints
# ============================================================

@app.get("/health")
def health():
    return {
        "ok": True,
        "version": app.version,
        "infer_workers": WORKERS,
        "gms_workers": GMS_WORKERS,
        "infer_queue_maxsize": QUEUE_MAXSIZE,
        "gms_queue_maxsize": GMS_QUEUE_MAXSIZE,
        "infer_qsize": infer_queue.qsize(),
        "gms_qsize": gms_queue.qsize(),
        "gpu_concurrency": GPU_CONCURRENCY,
        "model2_concurrency": MODEL2_CONCURRENCY,
        "gms_concurrency": GMS_CONCURRENCY,
        "hint_dedup_window_sec": HINT_DEDUP_WINDOW_SEC,
        "hint_near_dup_ratio": HINT_NEAR_DUP_RATIO,
        "hint_dedup_max_per_session": HINT_DEDUP_MAX_PER_SESSION,
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
        raise HTTPException(status_code=429, detail="Too many requests (infer queue busy/full)")

    try:
        result = await asyncio.wait_for(fut, timeout=REQUEST_MAX_WAIT)
        return result
    except asyncio.TimeoutError:
        log_error(
            "request_wait_timeout",
            session_id=session_id,
            infer_qsize=infer_queue.qsize(),
            gms_qsize=gms_queue.qsize(),
        )
        raise HTTPException(status_code=504, detail="Request timed out waiting in queue/stages")
    except HTTPException:
        raise
    except Exception as e:
        log_error("pipeline_failed", session_id=session_id, err=str(e), tb=traceback.format_exc()[-1500:])
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")
