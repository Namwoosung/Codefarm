# index.py  (A안: 1회 호출 + 안정 fallback + 과정 중심 + previous_judgement 원문 비노출 + AI 사용 점검 규칙 + "실수 요약(1~2문장)" 섹션)
import os
import re
import json
import hashlib
from typing import Optional, Literal, Dict, Any, List

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
MAX_COMPLETION_TOKENS = int(os.getenv("MAX_COMPLETION_TOKENS", "140"))
DEBUG_LOG = os.getenv("DEBUG_LOG", "1") == "1"

CACHE_SIZE = int(os.getenv("CACHE_SIZE", "512"))

TRUNC_PROBLEM_DESC = int(os.getenv("TRUNC_PROBLEM_DESC", "450"))
TRUNC_IO_DESC = int(os.getenv("TRUNC_IO_DESC", "200"))
TRUNC_CODE = int(os.getenv("TRUNC_CODE", "900"))

# 과정 중심: previous_judgement 많이 사용하되 "원문 노출 금지"
PREV_LIMIT = int(os.getenv("PREV_LIMIT", "12"))
PROCESS_BULLET_LIMIT = int(os.getenv("PROCESS_BULLET_LIMIT", "8"))

# ✅ 추가 규칙: 3분 이하 풀이시간이면 AI 사용 여부 점검
SUS_SOLVE_TIME_SEC = int(os.getenv("SUS_SOLVE_TIME_SEC", "180"))

app = FastAPI(title="Report Feedback Server", version="2.4.0")

_http_client: Optional[httpx.AsyncClient] = None
_cache: Dict[str, str] = {}
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
# Prompt (과정 중심 + 원문 노출 금지 + "실수 요약 1~2문장" 강제)
# =========================
DEVELOPER_PROMPT = """
Answer in Korean.
You are a kind and patient teacher speaking directly to a student.

TOP PRIORITY: the student's PROCESS (what they tried repeatedly / where they got stuck / how to improve next).
Use the JSON evidence fields: "mistake_summary" and (if present) "integrity_hint".
DO NOT quote or reveal any raw logs, English sentences, internal labels, or system/programming terms.

You MUST output ONLY the following markdown template.
You MUST start the output with exactly: "### ✅ 결과"
Do NOT write any text before that. Do NOT write any text after the template.

### ✅ 결과
- <한 줄: 과정 칭찬 중심 + **굵은 격려 1개 이상**>

### 🔍 앞으로 생각해볼 것
- <"지금까지 자주 실수한 부분"을 **1~2문장**으로 설명. 반드시 **굵은 표현 1개** 포함>

### 🛠 다음에 해볼 것
- <한 줄: **바로 할 행동 1** (과정 개선)>
- <한 줄: 행동 2>

Hard rules:
- Total <= 260 characters INCLUDING markdown and newlines.
- Exactly 3 headings and exactly 4 bullet lines (1 / 1 / 2).
- Use ONLY '**' for bold. No other markdown.
- No HTML tags, no code blocks, no backticks, no links.
""".strip()


# =========================
# Text utils
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


def _strip_forbidden_terms(text: str) -> str:
    text = text.replace("SUCCESS", "정답으로 통과")
    text = text.replace("GIVE_UP", "오류가 발생")
    for tok in FORBIDDEN_TOKENS:
        if tok in ("SUCCESS", "GIVE_UP"):
            continue
        if tok:
            text = text.replace(tok, "")
    text = LABEL_LIKE_PATTERN.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def _keep_from_first_heading(text: str) -> str:
    if not text:
        return text
    idx = text.find("### ✅ 결과")
    if idx == -1:
        return text
    return text[idx:].lstrip()


def postprocess(text: str) -> str:
    text = sanitize_llm_text(text)
    text = _keep_from_first_heading(text)
    text = _strip_forbidden_terms(text)

    lines = [ln.strip() for ln in (text or "").splitlines()]
    lines = [ln for ln in lines if ln]

    norm = []
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
    if not text.lstrip().startswith("### ✅ 결과"):
        return "PREFIX_TEXT_NOT_ALLOWED"

    if ASCII_HEAVY_RE.search(text):
        return "RAW_LOG_LEAK"

    for tok in FORBIDDEN_TOKENS:
        if tok and tok in text:
            return "INTERNAL_TERM_LEAK"
    if LABEL_LIKE_PATTERN.search(text):
        return "LABEL_LIKE_LEAK"

    required = ["### ✅ 결과", "### 🔍 앞으로 생각해볼 것", "### 🛠 다음에 해볼 것"]
    for h in required:
        if h not in text:
            return "MD_STRUCTURE_MISSING"

    headers = [ln for ln in text.splitlines() if ln.startswith("### ")]
    if len(headers) != 3:
        return "MD_TOO_MANY_HEADERS"

    bullets = [ln for ln in text.splitlines() if ln.startswith("- ")]
    if len(bullets) != 4:
        return "BULLET_COUNT_WRONG"

    # 결과 1개 + 앞으로생각해볼것 1개 + 다음행동(2개 중 최소 1개) => '**' 최소 6개 기대
    if text.count("**") < 6:
        return "BOLD_MISSING"

    # "앞으로 생각해볼 것" 한 불릿 안에 1~2문장 권장 검증(너무 강하게 잡으면 깨질 수 있어 약하게)
    # 마침표/느낌표/물음표 개수로 대략 판단
    lines = text.splitlines()
    try:
        idx = lines.index("### 🔍 앞으로 생각해볼 것")
        bullet = lines[idx + 1]
        sent_marks = sum(bullet.count(x) for x in [".", "!", "?", "요.", "다."])
        # 0이면 너무 단문일 가능성이 높음
        if sent_marks == 0:
            return "MISTAKE_SUMMARY_TOO_SHORT"
    except Exception:
        pass

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
    """
    LLM이 1~2문장으로 요약할 소재를 주기 위한 '학생용 근거 리스트'.
    - 원문 analysis는 정제 후 "간접표현"만
    - label_hints는 그대로(학생용)
    """
    out: List[str] = []
    seen = set()

    # 라벨 힌트 우선
    for h in (label_hints or []):
        if h and h not in seen:
            seen.add(h)
            out.append(h)
        if len(out) >= 6:
            return out

    # analysis에서 정제한 흔적 추가
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
        return "풀이 시간이 아주 짧고 코드가 한 번에 완성된 느낌이라, 다음엔 **스스로 먼저** 풀어보고 막힌 부분만 도움을 받아보자."
    return "풀이 시간이 아주 짧아서, 다음엔 **스스로 푼 과정**(중간 생각/메모)을 남기며 풀어보면 실력이 더 빨리 늘어."


# =========================
# Fallback (mistake_summary가 비어도 동작)
# =========================
def fallback_feedback(mistake_summary: List[str], rt: str, integrity_hint: Optional[str]) -> str:
    if rt == "SUCCESS":
        line1 = "- **끝까지 스스로 점검하며 마무리한 게 정말 좋아!**"
    else:
        line1 = "- **괜찮아, 과정에서 배우면 돼!** 이번엔 오류가 났어."

    if mistake_summary:
        ms = mistake_summary[0][:60] + ("…" if len(mistake_summary[0]) > 60 else "")
        line2 = f"- **지금까지 실수한 부분**은 {ms} 쪽이었어. 다음엔 그 순간에 값이 어떻게 바뀌는지 한 번 더 확인해보자."
    elif integrity_hint:
        line2 = f"- **지금까지 실수한 부분**을 기록이 없어서 추적하기 어려워. 대신 {integrity_hint}"
    else:
        line2 = "- **지금까지 실수한 부분**은 입력/조건/초기화에서 자주 생길 수 있어. 다음엔 한 가지씩만 골라서 차근차근 확인해보자."

    line3 = "- **작은 입력 1개**로 손으로 따라가며 중간값을 체크해봐."
    line4 = "- 같은 실수가 나오면, 그 줄 바로 위/아래에서 변수 값이 어떻게 바뀌는지 적어보자."

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
# Cache
# =========================
def make_cache_key(req: FeedbackRequest) -> str:
    pj_slice = req.previous_judgement[-PREV_LIMIT:]
    payload = {
        "p": {"title": req.problem.title, "difficulty": req.problem.difficulty, "algo": req.problem.algorithm},
        "u": {"lvl": req.user.coding_level, "age": req.user.age},
        "c": (req.code.content or "")[:400],
        "r": {"type": req.result.resultType, "solveTime": req.result.solveTime},
        "pj": [{"t": pj.judged_at, "a": (pj.analysis or "")[:120], "m": pj.mistake_type[:5]} for pj in pj_slice],
    }
    s = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _cache_get(key: str) -> Optional[str]:
    return _cache.get(key)


def _cache_put(key: str, value: str) -> None:
    if key in _cache:
        _cache[key] = value
        return
    _cache[key] = value
    _cache_order.append(key)
    if len(_cache_order) > CACHE_SIZE:
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
    if REQUIRE_SERVER_TOKEN and x_report_server_token != REPORT_SERVER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid server token")

    ck = make_cache_key(req)
    cached = _cache_get(ck)
    if cached is not None:
        if DEBUG_LOG:
            print(f"[CACHE HIT] request_id={req.request_id}")
        return {"request_id": req.request_id, "feedback": cached}

    recent_prev = req.previous_judgement[-PREV_LIMIT:]
    label_hints = summarize_labels_student_friendly(recent_prev, limit=5)

    # ✅ "실수 요약" 근거(학생용 소재)
    mistake_summary = build_mistake_summary(recent_prev, label_hints)

    # ✅ 근거가 비면 integrity 힌트
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

        # ✅ 학생 출력에 안전한 소재만
        "mistake_summary": mistake_summary,
        "integrity_hint": integrity_hint,

        "constraints": {
            "max_chars": MAX_FEEDBACK_CHARS,
            "template": "3 headings + 4 bullets (1/1/2)",
            "focus": "process-first",
            "forbidden": ["정답코드", "완전한 풀이", "코드블록", "백틱", "내부 필드명/라벨", "영문/로그 원문"],
        },
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "developer", "content": DEVELOPER_PROMPT},
            {
                "role": "user",
                "content": (
                    "다음 JSON만 보고 템플릿 그대로 작성해.\n"
                    "특히 '앞으로 생각해볼 것'에는 mistake_summary를 바탕으로 "
                    "'지금까지 자주 실수한 부분'을 **1~2문장**으로 써.\n"
                    "mistake_summary가 비어 있으면 integrity_hint를 사용해.\n"
                    "원문 인용/영문/로그는 절대 금지.\n"
                    "- 반드시: 3개 섹션 + 불릿 4줄(1/1/2) + 260자 이내\n\n"
                    + json.dumps(llm_payload, ensure_ascii=False)
                ),
            },
        ],
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
    }

    try:
        raw = await call_gms_once(payload)
        feedback_text = postprocess(raw)
        reason = policy_violation_reason(feedback_text)

        if DEBUG_LOG:
            print("[RAW]", raw)
            print("[POST]", feedback_text)
            print("[VIOLATION]", reason)
            print("[MISTAKE_SUMMARY]", mistake_summary)
            print("[INTEGRITY_HINT]", integrity_hint)

        if reason is not None:
            feedback_text = postprocess(fallback_feedback(mistake_summary, req.result.resultType, integrity_hint))
            if DEBUG_LOG:
                print("[FALLBACK]", feedback_text)

    except HTTPException as e:
        if DEBUG_LOG:
            print("[GMS ERROR FALLBACK]", e.detail)
        feedback_text = postprocess(fallback_feedback(mistake_summary, req.result.resultType, integrity_hint))

    _cache_put(ck, feedback_text)
    return {"request_id": req.request_id, "feedback": feedback_text}
