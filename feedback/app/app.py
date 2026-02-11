# index.py  (완화 캐시 적용 버전)
# 핵심 변경점:
# 1) 캐시 키를 "슬라이스 기반" -> "전체 해시 기반(Strict)"으로 변경하여
#    '비슷한 요청'이 아니라 '사실상 동일한 요청'에서만 캐시 HIT가 나도록 완화.
# 2) 캐시 스코프를 사용자 단위로 분리(user.id 포함)하여 사용자 간 피드백 섞임 방지.
# 3) (선택) TTL 도입: CACHE_TTL_SEC 초가 지나면 캐시 무효화(기본 10분).

import os
import re
import json
import time
import hashlib
from typing import Optional, Literal, Dict, Any, List, Tuple

import httpx
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# =========================
# Config
# =========================
GMS_URL = os.getenv("GMS_URL", "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions")
MODEL = os.getenv("GMS_MODEL", "gpt-4o-mini")

REQUIRE_SERVER_TOKEN = os.getenv("REQUIRE_SERVER_TOKEN", "0") == "1"
REPORT_SERVER_TOKEN = os.getenv("REPORT_SERVER_TOKEN", "")

HTTP_TIMEOUT = httpx.Timeout(
    float(os.getenv("HTTP_TIMEOUT_TOTAL", "12.0")),
    connect=float(os.getenv("HTTP_TIMEOUT_CONNECT", "3.0")),
)

MAX_FEEDBACK_CHARS = int(os.getenv("MAX_FEEDBACK_CHARS", "260"))

MAX_COMPLETION_TOKENS = int(os.getenv("MAX_COMPLETION_TOKENS", "320"))
if MAX_COMPLETION_TOKENS < 180:
    MAX_COMPLETION_TOKENS = 180

DEBUG_LOG = os.getenv("DEBUG_LOG", "1") == "1"

# ✅ 완화 캐시 설정
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "1") == "1"
CACHE_SIZE = int(os.getenv("CACHE_SIZE", "512"))
CACHE_TTL_SEC = int(os.getenv("CACHE_TTL_SEC", "600"))  # 기본 10분
# TTL을 끄고 싶으면 0으로
if CACHE_TTL_SEC < 0:
    CACHE_TTL_SEC = 0

TRUNC_PROBLEM_DESC = int(os.getenv("TRUNC_PROBLEM_DESC", "450"))
TRUNC_IO_DESC = int(os.getenv("TRUNC_IO_DESC", "200"))
TRUNC_CODE = int(os.getenv("TRUNC_CODE", "900"))

PREV_LIMIT = int(os.getenv("PREV_LIMIT", "12"))
PROCESS_BULLET_LIMIT = int(os.getenv("PROCESS_BULLET_LIMIT", "8"))

SUS_SOLVE_TIME_SEC = int(os.getenv("SUS_SOLVE_TIME_SEC", "180"))

RETURN_RAW = os.getenv("RETURN_RAW", "0") == "1"
USE_RESPONSE_FORMAT = os.getenv("USE_RESPONSE_FORMAT", "1") == "1"

app = FastAPI(title="Report Feedback Server", version="2.4.3-relaxed-cache")

_http_client: Optional[httpx.AsyncClient] = None

# ✅ 캐시: key -> (value, created_at_epoch)
_cache: Dict[str, Tuple[str, float]] = {}
_cache_order: List[str] = []


# =========================
# Schemas
# =========================
class Problem(BaseModel):
    title: str
    description: str
    input_description: str
    output_description: str
    difficulty: int = Field(..., ge=1, le=6)
    algorithm: str
    time_limit: float = Field(..., gt=0)
    memory_limit: int = Field(..., gt=0)


class User(BaseModel):
    id: int
    coding_level: int = Field(..., ge=1, le=5)
    age: int = Field(..., ge=5, le=120)


class Code(BaseModel):
    language: Literal["python"] = "python"
    content: str


class PreviousJudgement(BaseModel):
    analysis: str
    judged_at: str
    mistake_type: List[str] = Field(default_factory=list)


class Result(BaseModel):
    resultType: Literal["SUCCESS", "GIVE_UP"]
    solveTime: Optional[int] = Field(None, ge=0)
    execTime: Optional[int] = Field(None, ge=0)
    memory: Optional[int] = Field(None, ge=0)


class FeedbackRequest(BaseModel):
    request_id: Optional[str] = None
    problem: Problem
    user: User
    code: Code
    result: Result
    previous_judgement: List[PreviousJudgement] = Field(default_factory=list)


class FeedbackResponse(BaseModel):
    request_id: Optional[str] = None
    feedback: str


# =========================
# Label mapping (학생 친화 번역) - LLM 입력 요약에만 사용
# =========================
INTERNAL_TOKENS_BASE = ["SUCCESS", "GIVE_UP", "resultType", "mistake_type"]

LABEL_MAP: Dict[str, str] = {
    "Algorithm_BruteForce_NeedsOptimization": "방법은 맞는데 너무 느릴 수 있어서 더 빠른 방법을 고민해보면 좋아",
    "Algorithm_CompletelyWrong": "문제에서 원하는 방법과 풀이 방향이 조금 다른 쪽으로 가 있었어",
    "Boundary_Condition_Error": "가장 작은 값/가장 큰 값 같은 극단 상황에서 실수가 있었어",
    "Condition_Bug": "조건을 판단하는 부분에서 실수가 있었어",
    "DataType_Conversion_Error": "숫자와 글자를 바꾸는 과정에서 실수가 있었어",
    "DataType_String_Operation_Error": "문자열을 다루는 과정에서 실수가 있었어",
    "Index_Access_Error": "리스트에서 위치를 잘못 찾아가서 오류가 났을 가능성이 있어",
    "Input_DataType_Error": "입력 값을 숫자로 읽어야 하는데 형태가 헷갈렸던 적이 있어",
    "Input_Iteration_Error": "여러 줄 입력을 읽는 반복에서 실수가 있었어",
    "Input_MissingOrWrong": "필요한 입력을 빠뜨리거나 잘못 읽은 부분이 있었어",
    "Input_N_ZeroCase": "입력이 0개인 경우 처리가 약했던 적이 있어",
    "Input_Parsing_Error": "공백/줄바꿈을 나누는 과정에서 실수가 있었어",
    "Input_ReadOrder_Error": "입력을 읽는 순서가 꼬였던 적이 있어",
    "Input_T_MissingOrWrong": "맨 처음 테스트케이스 개수를 읽는 부분이 헷갈렸던 적이 있어",
    "Logic_Iteration_Error": "반복문이 너무 많이/적게 돌아서 결과가 달라졌을 가능성이 있어",
    "Logic_Order_Handling_Error": "처리 순서(먼저/나중)가 헷갈렸던 적이 있어",
    "Logic_Reset_Per_TestCase_Missing": "케이스가 바뀔 때 변수를 다시 초기화하지 못했던 적이 있어",
    "Logic_Result_Handling_Error": "결과를 저장/갱신하는 과정에서 실수가 있었어",
    "Logic_State_Reset_Error": "중간 상태를 초기화하는 타이밍이 어긋났던 적이 있어",
    "Logic_TestCase_Loop_Error": "테스트케이스 반복 처리에서 실수가 있었어",
    "Logic_ZeroCase_Handling_Error": "0/빈 상태 같은 특별한 경우 처리가 약했던 적이 있어",
    "NoCode_AfterMistake": "실수 후에 코드를 다시 정리해 이어가는 과정이 막혔던 적이 있어",
    "NoCode_AfterNoIssue": "전에는 잘 되다가 갑자기 코드가 거의 없는 상태로 바뀐 적이 있어",
    "NoCode_Persistent": "코드가 비어 있거나 거의 없는 상태가 계속 이어졌던 적이 있어",
    "No_Issue": "큰 실수 없이 잘 진행했어",
    "Output_EmptyCase_HandlingError": "출력할 게 없을 때 처리에서 실수가 있었어",
    "Output_Format_Error": "출력 형식(띄어쓰기/줄바꿈)을 헷갈렸던 적이 있어",
    "Output_Format_MissingCasePrefix": "케이스 번호 같은 출력 앞부분 표기를 빠뜨렸던 적이 있어",
    "Output_WrongYESNO": "YES/NO 출력 글자를 반대로 적었던 적이 있어",
    "Queue_Empty_Handling_Error": "비어 있을 때 처리(예외)가 빠졌던 적이 있어",
    "Queue_Order_Error": "들어온 순서대로 처리하는 부분이 헷갈렸던 적이 있어",
    "Queue_Peek_EmptyHandling": "맨 앞 값을 확인할 때 비어 있는 경우 처리가 약했던 적이 있어",
    "Reset_Initialization_Error": "변수 초기값 설정이 잘못되어 결과가 흔들렸던 적이 있어",
    "Stack_Empty_Handling_Error": "비어 있을 때 처리(예외)가 빠졌던 적이 있어",
    "Stack_Order_Error": "나중에 넣은 게 먼저 나오는 순서가 헷갈렸던 적이 있어",
    "Wrong_Target_Selection": "찾으라는 값/조건을 다른 것으로 착각했던 적이 있어",
}


def load_extra_labels() -> List[str]:
    labels_json = os.getenv("FEEDBACK_LABELS_JSON", "")
    if not labels_json.strip():
        return []
    try:
        arr = json.loads(labels_json)
        if isinstance(arr, list):
            return [str(x) for x in arr]
    except Exception:
        pass
    return []


EXTRA_LABELS = load_extra_labels()
FORBIDDEN_TOKENS = set(INTERNAL_TOKENS_BASE) | set(LABEL_MAP.keys()) | set(EXTRA_LABELS)
LABEL_LIKE_PATTERN = re.compile(r"\b[A-Z][A-Za-z0-9]*_(?:[A-Za-z0-9]+_?)+\b")


def explain_label_student_friendly(label: str) -> str:
    return LABEL_MAP.get(label, "기본 규칙(입력/출력/조건)을 확인하는 과정에서 작은 실수가 있었어")


def summarize_labels_student_friendly(prev: List["PreviousJudgement"], limit: int = 5) -> List[str]:
    out: List[str] = []
    for pj in prev:
        for lab in (pj.mistake_type or []):
            out.append(explain_label_student_friendly(str(lab)))
    seen = set()
    uniq = []
    for s in out:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq[:limit]


# =========================
# Prompt (JSON 응답: 섹션 분리) -> 서버가 마크다운 조립
# =========================
DEVELOPER_PROMPT = """
Answer in Korean.
You are a kind and patient teacher speaking directly to a student.

TOP PRIORITY: the student's PROCESS (what they tried repeatedly / where they got stuck / how to improve next).
Use the evidence fields: "mistake_summary" and (if present) "integrity_hint".
DO NOT quote or reveal any raw logs, English sentences, internal labels, or system/programming terms.

OUTPUT FORMAT (STRICT)
- Output must be ONE valid JSON object and nothing else.
- No markdown outside JSON. No code blocks. No backticks. No extra text.
- Use double quotes for all JSON strings.

The JSON MUST contain these keys (additional keys are allowed, but not required):
{
  "result": {
    "title": "string",
    "content": "string"
  },
  "think_next": {
    "title": "string",
    "content": "string"
  },
  "next_actions": {
    "title": "string",
    "items": ["string", "string"]
  }
}

Rules:
- result.content: 1 sentence, encouragement-focused.
- think_next.content: 1~2 sentences describing frequent past mistakes.
- next_actions.items: exactly 2 short action sentences.
- Do NOT include markdown in content strings.
- Keep it concise for a student.
""".strip()


# =========================
# Text utils (마크다운 조립 후 검사에 사용)
# =========================
CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
ASCII_HEAVY_RE = re.compile(r"[A-Za-z]{3,}")
_SPACE_RE = re.compile(r"\s+")


def _trunc(s: Optional[str], n: int) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[:n] + "…"


def sanitize_llm_text(text: str) -> str:
    text = text or ""
    text = CODE_FENCE_RE.sub("", text)
    text = text.replace("`", "")
    return text.strip()


def _keep_from_first_heading(text: str) -> str:
    if not text:
        return text
    idx = text.find("### ✅ 결과")
    if idx == -1:
        return text
    return text[idx:].lstrip()


def _strip_forbidden_terms_keep_lines(text: str) -> str:
    text = text.replace("SUCCESS", "정답으로 통과").replace("GIVE_UP", "오류가 발생")

    lines = text.splitlines()
    out_lines: List[str] = []
    for ln in lines:
        for tok in FORBIDDEN_TOKENS:
            if tok in ("SUCCESS", "GIVE_UP"):
                continue
            if tok:
                ln = ln.replace(tok, "")
        ln = LABEL_LIKE_PATTERN.sub("", ln)
        ln = re.sub(r"[ \t]+", " ", ln).strip()
        out_lines.append(ln)
    return "\n".join(out_lines).strip()


def postprocess(text: str) -> str:
    text = sanitize_llm_text(text)
    text = _keep_from_first_heading(text)
    text = _strip_forbidden_terms_keep_lines(text)

    lines = [ln.strip() for ln in (text or "").splitlines()]
    lines = [ln for ln in lines if ln]

    norm: List[str] = []
    for ln in lines:
        if ln.startswith("-") and not ln.startswith("- "):
            ln = "- " + ln[1:].lstrip()
        norm.append(ln)

    text = "\n".join(norm).strip()

    if len(text) > MAX_FEEDBACK_CHARS:
        text = text[:MAX_FEEDBACK_CHARS].rstrip()

    return text


def policy_violation_reason(text: str) -> Optional[str]:
    if not (text or "").strip():
        return "EMPTY"
    if len(text) > MAX_FEEDBACK_CHARS:
        return "TOO_LONG"
    if "```" in text or "`" in text:
        return "CODE_FORMAT"

    if ASCII_HEAVY_RE.search(text):
        return "RAW_LOG_LEAK"

    for tok in FORBIDDEN_TOKENS:
        if tok and tok in text:
            return "INTERNAL_TERM_LEAK"
    if LABEL_LIKE_PATTERN.search(text):
        return "LABEL_LIKE_LEAK"

    return None


# =========================
# Process summarization -> mistake_summary (학생용 1~2문장 소재)
# =========================
RAW_NOISE_PATTERNS = [
    re.compile(r"```.*?```", re.DOTALL),
    re.compile(r"[A-Za-z]{3,}"),
    re.compile(r"[(){}\[\];<>]"),
    re.compile(r"\d{4}-\d{2}-\d{2}"),
]


def _clean_process_text(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    for p in RAW_NOISE_PATTERNS:
        s = p.sub(" ", s)
    s = _SPACE_RE.sub(" ", s).strip()
    if len(s) < 10:
        return ""
    return s


def build_mistake_summary(prev: List[PreviousJudgement], label_hints: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()

    for h in (label_hints or []):
        if h and h not in seen:
            seen.add(h)
            out.append(h)
        if len(out) >= 6:
            return out

    for pj in reversed(prev):
        cleaned = _clean_process_text(pj.analysis)
        if not cleaned:
            continue
        cleaned = cleaned[:70] + ("…" if len(cleaned) > 70 else "")
        cand = f"{cleaned}에서 자주 멈칫했어"
        key = cand.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(cand)
        if len(out) >= 6:
            return out

    return out[:6]


# =========================
# Academic integrity helper (근거가 없을 때)
# =========================
def solve_time_suspicious(req: FeedbackRequest) -> bool:
    if req.result.resultType != "SUCCESS":
        return False
    if req.result.solveTime is None:
        return False
    return req.result.solveTime <= SUS_SOLVE_TIME_SEC


def code_looks_ai_generated(code: str) -> bool:
    c = (code or "").strip()
    if not c:
        return False
    lines = [ln.rstrip() for ln in c.splitlines() if ln.strip()]
    if len(lines) < 6:
        return False

    long_comment = sum(1 for ln in lines if ln.lstrip().startswith("#") and len(ln) >= 60)
    docstring_like = sum(1 for ln in lines if ('"""' in ln or "'''" in ln))
    generic_phrases = 0
    for kw in [
        "Time complexity", "space complexity", "edge case", "optimize", "robust", "generic",
        "이 코드는", "다음과 같이", "핵심 아이디어", "시간 복잡도", "예외 처리",
    ]:
        if kw.lower() in c.lower():
            generic_phrases += 1

    if long_comment >= 2:
        return True
    if docstring_like >= 2 and len(lines) >= 25:
        return True
    if generic_phrases >= 3 and len(lines) >= 20:
        return True
    return False


def build_integrity_hint(req: FeedbackRequest) -> Optional[str]:
    if not solve_time_suspicious(req):
        return None
    if code_looks_ai_generated(req.code.content):
        return "풀이 시간이 아주 짧고 코드가 한 번에 완성된 느낌이라, 다음엔 스스로 먼저 풀어보고 막힌 부분만 도움을 받아보자."
    return "풀이 시간이 아주 짧아서, 다음엔 스스로 푼 과정(중간 생각/메모)을 남기며 풀어보면 실력이 더 빨리 늘어."


# =========================
# Fallback
# =========================
def fallback_feedback(mistake_summary: List[str], rt: str, integrity_hint: Optional[str]) -> str:
    if rt == "SUCCESS":
        line1 = "- 끝까지 스스로 점검하며 마무리한 게 정말 좋아!"
    else:
        line1 = "- 괜찮아, 과정에서 배우면 돼! 이번엔 오류가 났어."

    if mistake_summary:
        ms = mistake_summary[0][:60] + ("…" if len(mistake_summary[0]) > 60 else "")
        line2 = f"- 지금까지 자주 헷갈린 부분은 {ms}였어. 다음엔 그 순간에 값이 어떻게 바뀌는지 한 번 더 확인해보자."
    elif integrity_hint:
        line2 = f"- 과정 기록이 거의 없어서 자주 실수한 지점을 딱 집기 어려워. 대신 {integrity_hint}"
    else:
        line2 = "- 지금까지 자주 헷갈린 부분은 입력/조건/초기화에서 생기기 쉬워. 다음엔 한 가지씩만 골라 차근차근 확인해보자."

    line3 = "- 작은 입력 1개로 손으로 따라가며 중간값을 체크해봐."
    line4 = "- 같은 실수가 나오면, 그 줄 바로 위/아래에서 변수 값 변화를 한 줄로 적어보자."

    return "\n".join([
        "### ✅ 결과",
        line1,
        "",
        "### 🔍 앞으로 생각해볼 것",
        line2,
        "",
        "### 🛠 다음에 해볼 것",
        line3,
        line4,
    ])


# =========================
# ✅ 완화 캐시(Strict key + TTL + user scope)
# =========================
def _sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def make_cache_key(req: FeedbackRequest) -> str:
    """
    완화 캐시(=보수적 캐시):
    - '비슷한 요청'이 아니라 '사실상 동일한 요청'에서만 캐시 HIT가 나도록
      슬라이스 대신 전체 해시를 사용.
    - user.id 포함: 사용자 간 캐시 섞임 방지.
    - problem description/input/output 포함: 같은 title이라도 내용이 다르면 MISS.
    """
    pj_slice = req.previous_judgement[-PREV_LIMIT:]
    payload = {
        "u": {"id": req.user.id, "lvl": req.user.coding_level, "age": req.user.age},
        "p": {
            "title": req.problem.title,
            "difficulty": req.problem.difficulty,
            "algo": req.problem.algorithm,
            "desc_h": _sha256_text(req.problem.description),
            "in_h": _sha256_text(req.problem.input_description),
            "out_h": _sha256_text(req.problem.output_description),
        },
        "c": {
            "lang": req.code.language,
            "content_h": _sha256_text(req.code.content),
            "len": len(req.code.content or ""),
        },
        "r": {"type": req.result.resultType, "solveTime": req.result.solveTime},
        "pj": [
            {
                "t": pj.judged_at,
                "analysis_h": _sha256_text(pj.analysis),
                "m": sorted([str(x) for x in (pj.mistake_type or [])]),
            }
            for pj in pj_slice
        ],
    }
    s = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _cache_is_expired(created_at: float) -> bool:
    if CACHE_TTL_SEC == 0:
        return False
    return (time.time() - created_at) > CACHE_TTL_SEC


def _cache_get(key: str) -> Optional[str]:
    if not CACHE_ENABLED:
        return None
    item = _cache.get(key)
    if item is None:
        return None
    value, created_at = item
    if _cache_is_expired(created_at):
        # 만료된 항목 제거
        _cache.pop(key, None)
        try:
            _cache_order.remove(key)
        except ValueError:
            pass
        if DEBUG_LOG:
            print(f"[CACHE EXPIRED] key={key[:8]}")
        return None
    return value


def _cache_put(key: str, value: str) -> None:
    if not CACHE_ENABLED:
        return

    now = time.time()

    if key in _cache:
        _cache[key] = (value, now)
        return

    _cache[key] = (value, now)
    _cache_order.append(key)

    # 용량 초과 시 evict
    while len(_cache_order) > CACHE_SIZE:
        old = _cache_order.pop(0)
        _cache.pop(old, None)


# =========================
# HTTP client
# =========================
async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
        _http_client = httpx.AsyncClient(timeout=HTTP_TIMEOUT, limits=limits)
    return _http_client


@app.on_event("shutdown")
async def shutdown_event():
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


# =========================
# GMS call (A안: 1회 호출)
# =========================
async def call_gms_once(payload: dict) -> str:
    api_key = os.getenv("GMS_API_KEY") or os.getenv("GMS_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing GMS_API_KEY (or GMS_KEY)")

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    client = await get_http_client()

    r = await client.post(GMS_URL, headers=headers, json=payload)
    if r.status_code != 200:
        if DEBUG_LOG:
            print("GMS STATUS:", r.status_code)
            print("GMS BODY:", (r.text or "")[:2000])
        raise HTTPException(status_code=502, detail=f"GMS error {r.status_code}: {r.text}")

    data = r.json()
    if DEBUG_LOG:
        print("[GMS 200 FULL SNIP]", json.dumps(data, ensure_ascii=False)[:2000])

    try:
        choice0 = data["choices"][0]
        msg = choice0["message"]
        content = msg.get("content", None)
        finish_reason = choice0.get("finish_reason", None)
    except Exception:
        raise HTTPException(status_code=502, detail=f"Unexpected GMS response: {data}")

    if DEBUG_LOG:
        print("[GMS finish_reason]", finish_reason)
        print("[GMS message keys]", list(msg.keys()))
        print("[GMS refusal]", msg.get("refusal", None))

    if content is None or str(content).strip() == "":
        raise HTTPException(status_code=502, detail="GMS returned empty content")

    return str(content)


# =========================
# Routes
# =========================
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/v1/reports/feedback", response_model=FeedbackResponse)
async def feedback(
    req: FeedbackRequest,
    x_report_server_token: Optional[str] = Header(None, alias="X-REPORT-SERVER-TOKEN"),
):
    # -------------------------
    # 1) Auth
    # -------------------------
    if REQUIRE_SERVER_TOKEN and x_report_server_token != REPORT_SERVER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid server token")

    # -------------------------
    # 2) Cache (완화 캐시: strict key + TTL + user scope)
    # -------------------------
    ck = make_cache_key(req)

    # 원본 확인 모드에서는 캐시 우회
    if (not RETURN_RAW) and CACHE_ENABLED:
        cached = _cache_get(ck)
        if cached is not None:
            if DEBUG_LOG:
                print(f"[CACHE HIT] request_id={req.request_id} key={ck[:8]} ttl={CACHE_TTL_SEC}s")
            return {"request_id": req.request_id, "feedback": cached}

    # -------------------------
    # 3) Evidence build
    # -------------------------
    recent_prev = req.previous_judgement[-PREV_LIMIT:]
    label_hints = summarize_labels_student_friendly(recent_prev, limit=5)
    mistake_summary = build_mistake_summary(recent_prev, label_hints)

    integrity_hint = None
    if (not recent_prev) or (not mistake_summary):
        integrity_hint = build_integrity_hint(req)

    llm_payload = {
        "tone_hint": "친근하지만 핵심 위주의 코칭 톤",
        "problem": {
            "title": req.problem.title,
            "difficulty": req.problem.difficulty,
            "algorithm": req.problem.algorithm,
            "description": _trunc(req.problem.description, TRUNC_PROBLEM_DESC),
            "input_description": _trunc(req.problem.input_description, TRUNC_IO_DESC),
            "output_description": _trunc(req.problem.output_description, TRUNC_IO_DESC),
        },
        "user": {"age": req.user.age, "coding_level": req.user.coding_level},
        "code": {"language": req.code.language, "content": _trunc(req.code.content, TRUNC_CODE)},
        "result": {"resultType": req.result.resultType},
        "mistake_summary": mistake_summary,
        "integrity_hint": integrity_hint,
        "constraints": {
            "max_chars": MAX_FEEDBACK_CHARS,
            "focus": "process-first",
            "forbidden": ["정답코드", "완전한 풀이", "코드블록", "백틱", "내부 필드명/라벨", "영문/로그 원문"],
        },
    }

    # -------------------------
    # 4) Build GMS payload
    # -------------------------
    gms_payload: Dict[str, Any] = {
        "model": MODEL,
        "messages": [
            {"role": "developer", "content": DEVELOPER_PROMPT},
            {
                "role": "user",
                "content": (
                    "아래 JSON 근거만 보고, 요구한 JSON 스키마로만 답해.\n"
                    "- result/think_next/next_actions를 반드시 채워.\n"
                    "- think_next.content는 mistake_summary를 바탕으로 '지금까지 자주 실수한 부분'을 1~2문장으로.\n"
                    "- mistake_summary가 비어 있으면 integrity_hint로 대체.\n"
                    "- 입력/초기화/예외 처리 같은 일반적인 조언은 코드에 근거가 있을 때만 언급해.\n"
                    "- 원문 인용/영문/로그/내부 라벨 금지.\n\n"
                    + json.dumps(llm_payload, ensure_ascii=False)
                ),
            },
        ],
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
    }

    if USE_RESPONSE_FORMAT:
        gms_payload["response_format"] = {"type": "json_object"}

    # -------------------------
    # 5) Call + parse (명확한 JSON 파싱 실패 감지)
    # -------------------------
    def _try_parse_json_object(raw: str) -> Optional[Dict[str, Any]]:
        try:
            obj = json.loads(raw)
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

    try:
        raw = await call_gms_once(gms_payload)

        if RETURN_RAW:
            if DEBUG_LOG:
                print("[RETURN_RAW=1] raw only")
                print("[RAW]", raw[:2000])
                print("[MISTAKE_SUMMARY]", mistake_summary)
                print("[INTEGRITY_HINT]", integrity_hint)
                print("[MAX_COMPLETION_TOKENS]", MAX_COMPLETION_TOKENS, "USE_RESPONSE_FORMAT=", USE_RESPONSE_FORMAT)
            return {"request_id": req.request_id, "feedback": raw}

        obj = _try_parse_json_object(raw)
        if obj is None:
            if DEBUG_LOG:
                print("[RAW]", raw[:2000])
                print("[PARSE]", "JSON_PARSE_ERROR")
                print("[MAX_COMPLETION_TOKENS]", MAX_COMPLETION_TOKENS, "USE_RESPONSE_FORMAT=", USE_RESPONSE_FORMAT)
                print("[MISTAKE_SUMMARY]", mistake_summary)
                print("[INTEGRITY_HINT]", integrity_hint)

            feedback_text = postprocess(fallback_feedback(mistake_summary, req.result.resultType, integrity_hint))
            _cache_put(ck, feedback_text)
            return {"request_id": req.request_id, "feedback": feedback_text}

        # -------------------------
        # 6) Assemble markdown (title은 서버에서 고정)
        # -------------------------
        result = obj.get("result") or {}
        think_next = obj.get("think_next") or {}
        next_actions = obj.get("next_actions") or {}

        if not isinstance(result, dict):
            result = {}
        if not isinstance(think_next, dict):
            think_next = {}
        if not isinstance(next_actions, dict):
            next_actions = {}

        r_content = (result.get("content") or "").strip()
        t_content = (think_next.get("content") or "").strip()

        items = next_actions.get("items") or []
        if not isinstance(items, list):
            items = []
        item1 = (items[0] if len(items) > 0 else "").strip()
        item2 = (items[1] if len(items) > 1 else "").strip()

        raw_md = "\n".join([
            "### ✅ 결과",
            f"- {r_content}" if r_content else "-",
            "",
            "### 🔍 앞으로 생각해볼 것",
            f"- {t_content}" if t_content else "-",
            "",
            "### 🛠 다음에 해볼 것",
            f"- {item1}" if item1 else "-",
            f"- {item2}" if item2 else "-",
        ])

        feedback_text = postprocess(raw_md)
        reason = policy_violation_reason(feedback_text)

        if DEBUG_LOG:
            print("[RAW JSON OK]", json.dumps(obj, ensure_ascii=False)[:2000])
            print("[ASSEMBLED MD]", raw_md)
            print("[POST]", feedback_text)
            print("[VIOLATION]", reason)
            print("[MAX_COMPLETION_TOKENS]", MAX_COMPLETION_TOKENS, "USE_RESPONSE_FORMAT=", USE_RESPONSE_FORMAT)
            print("[MISTAKE_SUMMARY]", mistake_summary)
            print("[INTEGRITY_HINT]", integrity_hint)

        if reason is not None:
            feedback_text = postprocess(fallback_feedback(mistake_summary, req.result.resultType, integrity_hint))
            if DEBUG_LOG:
                print("[FALLBACK]", feedback_text)

    except HTTPException as e:
        if DEBUG_LOG:
            print("[GMS ERROR]", e.detail)
            print("[MAX_COMPLETION_TOKENS]", MAX_COMPLETION_TOKENS, "USE_RESPONSE_FORMAT=", USE_RESPONSE_FORMAT)

        if RETURN_RAW:
            return {"request_id": req.request_id, "feedback": f"[GMS ERROR] {e.detail}"}

        feedback_text = postprocess(fallback_feedback(mistake_summary, req.result.resultType, integrity_hint))

    except Exception as e:
        if DEBUG_LOG:
            print("[UNEXPECTED ERROR]", repr(e))
            print("[MAX_COMPLETION_TOKENS]", MAX_COMPLETION_TOKENS, "USE_RESPONSE_FORMAT=", USE_RESPONSE_FORMAT)

        if RETURN_RAW:
            return {"request_id": req.request_id, "feedback": f"[UNEXPECTED ERROR] {repr(e)}"}

        feedback_text = postprocess(fallback_feedback(mistake_summary, req.result.resultType, integrity_hint))

    if not RETURN_RAW:
        _cache_put(ck, feedback_text)

    return {"request_id": req.request_id, "feedback": feedback_text}
