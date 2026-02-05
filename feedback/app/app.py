# index.py  (A안: gpt-5.2(또는 5.1) 단독 + 1회 호출 + 안정 fallback + 라벨 자동 매핑/제거)
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
MODEL = os.getenv("GMS_MODEL", "gpt-5.2")

REQUIRE_SERVER_TOKEN = os.getenv("REQUIRE_SERVER_TOKEN", "0") == "1"
REPORT_SERVER_TOKEN = os.getenv("REPORT_SERVER_TOKEN", "")

HTTP_TIMEOUT = httpx.Timeout(
    float(os.getenv("HTTP_TIMEOUT_TOTAL", "12.0")),
    connect=float(os.getenv("HTTP_TIMEOUT_CONNECT", "3.0")),
)

# ✅ A안: 비용 폭주 방지 — 재시도/재생성 전부 OFF
MAX_FEEDBACK_CHARS = int(os.getenv("MAX_FEEDBACK_CHARS", "260"))
# 260자 제한이면 220 토큰은 과한 편이라 줄여서 장문 폭주를 낮춥니다.
MAX_COMPLETION_TOKENS = int(os.getenv("MAX_COMPLETION_TOKENS", "140"))
DEBUG_LOG = os.getenv("DEBUG_LOG", "1") == "1"

CACHE_SIZE = int(os.getenv("CACHE_SIZE", "512"))

TRUNC_PROBLEM_DESC = int(os.getenv("TRUNC_PROBLEM_DESC", "450"))
TRUNC_IO_DESC = int(os.getenv("TRUNC_IO_DESC", "200"))
TRUNC_CODE = int(os.getenv("TRUNC_CODE", "1400"))
TRUNC_PREV_ANALYSIS = int(os.getenv("TRUNC_PREV_ANALYSIS", "150"))
PREV_LIMIT = int(os.getenv("PREV_LIMIT", "2"))

app = FastAPI(title="Report Feedback Server", version="2.1.2")

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
# Label mapping (학생 친화 번역)
# =========================
INTERNAL_TOKENS_BASE = ["SUCCESS", "GIVE_UP", "resultType", "mistake_type"]

LABEL_MAP: Dict[str, str] = {
    # Algorithm / Approach
    "Algorithm_BruteForce_NeedsOptimization": "방법은 맞는데 너무 느릴 수 있어서 더 빠른 방법을 고민해보면 좋아",
    "Algorithm_CompletelyWrong": "문제에서 원하는 방법과 풀이 방향이 조금 다른 쪽으로 가 있었어",

    # Boundary / Condition
    "Boundary_Condition_Error": "가장 작은 값/가장 큰 값 같은 극단 상황에서 실수가 있었어",
    "Condition_Bug": "조건을 판단하는 부분에서 실수가 있었어",

    # DataType
    "DataType_Conversion_Error": "숫자와 글자를 바꾸는(변환하는) 과정에서 실수가 있었어",
    "DataType_String_Operation_Error": "문자열을 다루는 과정(붙이기/자르기/비교)에서 실수가 있었어",

    # Index / Access
    "Index_Access_Error": "배열(리스트)에서 위치를 잘못 찾아가서 오류가 났을 가능성이 있어",

    # Input
    "Input_DataType_Error": "입력 값을 숫자로 읽어야 하는데 글자로 처리하는 등 입력 형태가 헷갈렸던 적이 있어",
    "Input_Iteration_Error": "입력을 여러 줄/여러 개 읽는 반복에서 실수가 있었어",
    "Input_MissingOrWrong": "필요한 입력을 빠뜨리거나 잘못 읽은 부분이 있었어",
    "Input_N_ZeroCase": "입력이 0개일 때(빈 경우)를 처리하는 부분이 약했던 적이 있어",
    "Input_Parsing_Error": "공백/줄바꿈을 나눠 읽는 과정에서 실수가 있었어",
    "Input_ReadOrder_Error": "입력을 읽는 순서가 꼬였던 적이 있어",
    "Input_T_MissingOrWrong": "테스트케이스 개수(맨 처음 숫자)를 읽는 부분이 헷갈렸던 적이 있어",

    # Logic (iteration / order / state)
    "Logic_Iteration_Error": "반복문이 너무 많이/너무 적게 돌아서 결과가 달라졌을 가능성이 있어",
    "Logic_Order_Handling_Error": "처리해야 할 순서(앞/뒤, 먼저/나중)가 헷갈렸던 적이 있어",
    "Logic_Queue_Implementation_Inefficient": "큐(줄 서기) 방식은 맞는데 구현이 비효율적이라 느려질 수 있어",
    "Logic_Reset_Per_TestCase_Missing": "테스트케이스가 바뀔 때 변수를 다시 초기화하지 못했던 적이 있어",
    "Logic_Result_Handling_Error": "계산한 결과를 저장/갱신/출력하는 과정에서 실수가 있었어",
    "Logic_State_Reset_Error": "중간 상태(플래그/합/인덱스)를 다시 초기화하는 타이밍이 어긋났던 적이 있어",
    "Logic_TestCase_Loop_Error": "테스트케이스 반복 처리(케이스 수만큼 돌기)에서 실수가 있었어",
    "Logic_ZeroCase_Handling_Error": "특별한 경우(0, 빈 상태, 아무것도 선택 안 함)를 처리하는 규칙이 약했던 적이 있어",

    # NoCode / Progress
    "NoCode_AfterMistake": "실수 이후에 코드를 다시 정리해서 이어가는 과정이 막혔던 적이 있어",
    "NoCode_AfterNoIssue": "전에는 잘 되다가 갑자기 코드가 거의 없는 상태로 바뀐 적이 있어",
    "NoCode_Persistent": "코드가 비어 있거나 거의 없는 상태가 계속 이어졌던 적이 있어",

    # No issue
    "No_Issue": "큰 실수 없이 잘 진행했어",

    # Output
    "Output_EmptyCase_HandlingError": "출력해야 할 게 없을 때(빈 경우) 처리/출력에서 실수가 있었어",
    "Output_Format_Error": "출력 형식(띄어쓰기/줄바꿈/케이스 표기)을 조금 헷갈렸던 적이 있어",
    "Output_Format_MissingCasePrefix": "케이스 번호 같은 출력 앞부분 표기를 빠뜨렸던 적이 있어",
    "Output_WrongYESNO": "YES/NO 같은 출력 글자를 반대로 적거나 다르게 적었던 적이 있어",

    # Queue
    "Queue_Empty_Handling_Error": "큐가 비어 있을 때 처리(예외 상황)가 빠졌던 적이 있어",
    "Queue_Order_Error": "큐에서 들어온 순서대로 처리하는 부분이 헷갈렸던 적이 있어",
    "Queue_Peek_EmptyHandling": "큐의 맨 앞 값을 확인할 때, 비어 있는 경우 처리가 약했던 적이 있어",

    # Reset / Init
    "Reset_Initialization_Error": "변수 초기값(처음 값) 설정이 잘못되어 결과가 흔들렸던 적이 있어",

    # Stack
    "Stack_Empty_Handling_Error": "스택이 비어 있을 때 처리(예외 상황)가 빠졌던 적이 있어",
    "Stack_Order_Error": "스택의 LIFO(나중에 넣은 게 먼저 나오는 순서) 부분이 헷갈렸던 적이 있어",

    # Wrong target
    "Wrong_Target_Selection": "문제에서 찾으라는 값/조건을 다른 것으로 착각했던 적이 있어",
}

# (선택) 환경변수로 추가 라벨이 오면 여기도 흡수
# 예) .env
# FEEDBACK_LABELS_JSON=["NoCode_Early","Input_T_MissingOrWrong","Output_Format_MissingCasePrefix"]
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


def summarize_mistakes_student_friendly(prev: List["PreviousJudgement"]) -> List[str]:
    out: List[str] = []
    for pj in prev:
        for lab in (pj.mistake_type or []):
            out.append(explain_label_student_friendly(str(lab)))

    # 중복 제거(순서 유지)
    seen = set()
    uniq = []
    for s in out:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq[:5]


# =========================
# Prompt (형식 강제)
# =========================
DEVELOPER_PROMPT = """
Answer in Korean. You are a kind and patient teacher speaking directly to a student.

You MUST output ONLY the following markdown template.
You MUST start the output with exactly: "### ✅ 결과"
Do NOT write any text before that. Do NOT write any text after the template.

### ✅ 결과
- <한 줄: 결과 요약 + **굵은 격려 1개 이상**>

### 🔍 근거(왜 이렇게 됐을까?)
- <한 줄: **핵심 원인 1개** 강조 + 학생 말>

### 🛠 다음에 해볼 것
- <한 줄: **바로 할 행동 1**>
- <한 줄: 행동 2>

Hard rules:
- Total <= 260 characters INCLUDING markdown and newlines.
- Exactly 3 headings (above) and exactly 4 bullet lines (1 / 1 / 2).
- Use ONLY '**' for bold. No other markdown.
- No HTML tags, no code blocks, no backticks, no links.
- NEVER mention internal field names, labels, codes, or system/programming terms.
""".strip()


# =========================
# Text utils
# =========================
CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)

def _trunc(s: Optional[str], n: int) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[:n] + "…"


def sanitize_llm_text(text: str) -> str:
    text = text or ""
    text = CODE_FENCE_RE.sub("", text)
    text = text.replace("`", "")
    return text.strip()


def _strip_forbidden_terms(text: str) -> str:
    # 1) 치환(의미만 남기기)
    text = text.replace("SUCCESS", "정답으로 통과")
    text = text.replace("GIVE_UP", "오류가 발생")

    # 2) 내부 토큰/라벨 제거
    for tok in FORBIDDEN_TOKENS:
        if tok in ("SUCCESS", "GIVE_UP"):
            continue
        if tok:
            text = text.replace(tok, "")

    # 3) 라벨처럼 보이는 패턴도 제거(유출 방지)
    text = LABEL_LIKE_PATTERN.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def _keep_from_first_heading(text: str) -> str:
    """
    모델이 '줄글 + 템플릿' 형태로 출력하는 경우가 잦아,
    템플릿 시작(### ✅ 결과) 이전의 모든 텍스트를 잘라냅니다.
    """
    if not text:
        return text
    idx = text.find("### ✅ 결과")
    if idx == -1:
        return text
    return text[idx:].lstrip()


def postprocess(text: str) -> str:
    text = sanitize_llm_text(text)

    # ✅ 0) 템플릿 시작 이전의 줄글 제거
    text = _keep_from_first_heading(text)

    # ✅ 1) 내부 용어/라벨 유출 방지
    text = _strip_forbidden_terms(text)

    # ✅ 2) 줄바꿈 보존하면서 정리
    lines = [ln.strip() for ln in (text or "").splitlines()]
    lines = [ln for ln in lines if ln]  # 빈 줄 제거

    norm = []
    for ln in lines:
        # "-내용" -> "- 내용"
        if ln.startswith("-") and not ln.startswith("- "):
            ln = "- " + ln[1:].lstrip()
        norm.append(ln)

    text = "\n".join(norm).strip()

    # ✅ 3) 260자 제한(하드컷)
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

    # ✅ 템플릿 시작 강제(전처리에서 잘라냈더라도 최종 확인)
    if not text.lstrip().startswith("### ✅ 결과"):
        return "PREFIX_TEXT_NOT_ALLOWED"

    # 토큰 유출 최후 검사
    for tok in FORBIDDEN_TOKENS:
        if tok and tok in text:
            return "INTERNAL_TERM_LEAK"
    if LABEL_LIKE_PATTERN.search(text):
        return "LABEL_LIKE_LEAK"

    # ✅ 마크다운 구조 검사
    required = ["### ✅ 결과", "### 🔍 근거(왜 이렇게 됐을까?)", "### 🛠 다음에 해볼 것"]
    for h in required:
        if h not in text:
            return "MD_STRUCTURE_MISSING"

    headers = [ln for ln in text.splitlines() if ln.startswith("### ")]
    if len(headers) != 3:
        return "MD_TOO_MANY_HEADERS"

    bullets = [ln for ln in text.splitlines() if ln.startswith("- ")]
    if len(bullets) != 4:
        return "BULLET_COUNT_WRONG"

    # 굵은 표현 최소 3군데(결과/근거/다음행동 중 최소 1개 강조가 자연스럽게 나오도록)
    # '**' 토큰이 6개면(쌍 3개) OK
    if text.count("**") < 6:
        return "BOLD_MISSING"

    return None


# =========================
# Domain helpers
# =========================
def tone_hint(user: User, problem: Problem) -> str:
    if user.coding_level <= 2 or user.age <= 14:
        return "아주 친근하고 쉬운 표현으로 단계적으로 설명"
    if problem.difficulty >= 4:
        return "간결하고 정형화된 코칭 톤"
    return "친근하지만 핵심 위주의 코칭 톤"


def _result_type_korean(rt: str) -> str:
    return "정답으로 통과" if rt == "SUCCESS" else "오류 발생"


def fallback_feedback(req: FeedbackRequest) -> str:
    """
    fallback도 동일한 '3개 헤더 + 4개 불릿' 형식을 지켜야 policy 통과가 쉬움.
    """
    rt = req.result.resultType
    gap = req.problem.difficulty - req.user.coding_level

    if rt == "SUCCESS":
        line1 = "- **정답으로 통과했어!** 끝까지 해결한 게 정말 좋아."
        line2 = "- **입력/출력 형식**을 한 번 더 점검하면 더 깔끔해져."
        line3 = "- **작은 예시 1개**로 손으로 따라가며 중간값을 확인해봐."
        line4 = "- 다음엔 같은 유형을 1문제 더 풀어서 패턴을 익혀보자."
    else:
        line1 = "- **괜찮아, 여기서 배우면 돼!** 이번엔 오류가 났어."
        if gap >= 2:
            cause = "**입력 처리/조건**에서 헷갈렸을 가능성이 커."
        else:
            cause = "**변수 초기화/조건** 중 한 군데가 어긋났을 가능성이 있어."
        line2 = f"- {cause} 한 곳만 찍어서 확인해보자."
        line3 = "- **가장 작은 입력**으로 직접 값을 써가며 흐름을 확인해봐."
        line4 = "- 출력이 맞는지(YES/NO, 줄바꿈)도 마지막에 한 번 점검해봐."

    fb = "\n".join([
        "### ✅ 결과",
        line1,
        "",
        "### 🔍 근거(왜 이렇게 됐을까?)",
        line2,
        "",
        "### 🛠 다음에 해볼 것",
        line3,
        line4
    ])
    return fb


# =========================
# Cache
# =========================
def make_cache_key(req: FeedbackRequest) -> str:
    payload = {
        "p": {"title": req.problem.title, "difficulty": req.problem.difficulty, "algo": req.problem.algorithm},
        "u": {"lvl": req.user.coding_level, "age": req.user.age},
        "c": (req.code.content or "")[:800],
        "r": {"type": req.result.resultType},
        "pj": [{"t": pj.judged_at, "m": pj.mistake_type} for pj in req.previous_judgement[-PREV_LIMIT:]],
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
    if REQUIRE_SERVER_TOKEN:
        if x_report_server_token != REPORT_SERVER_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid server token")

    ck = make_cache_key(req)
    cached = _cache_get(ck)
    if cached is not None:
        if DEBUG_LOG:
            print(f"[CACHE HIT] request_id={req.request_id}")
        return {"request_id": req.request_id, "feedback": cached}

    gap = req.problem.difficulty - req.user.coding_level
    if DEBUG_LOG:
        print(f"[REQ] request_id={req.request_id} gap={gap} result={_result_type_korean(req.result.resultType)}")

    recent_prev = req.previous_judgement[-PREV_LIMIT:]

    # ✅ LLM에 라벨 원문을 직접 주지 않고, 학생용 요약 문장으로 변환
    prev_student_friendly = summarize_mistakes_student_friendly(recent_prev)

    prev_payload = [
        {
            "judged_at": pj.judged_at,
            "analysis": _trunc(pj.analysis, TRUNC_PREV_ANALYSIS),
        }
        for pj in recent_prev
    ]

    # result 축약(GIVE_UP이면 성능지표 제외)
    if req.result.resultType == "GIVE_UP":
        result_payload = {"resultType": "GIVE_UP"}
    else:
        result_payload = {
            "resultType": "SUCCESS",
            "solveTime": req.result.solveTime,
            "execTime": req.result.execTime,
            "memory": req.result.memory,
        }

    llm_payload = {
        "tone_hint": tone_hint(req.user, req.problem),
        "difficulty_gap": gap,
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
        "result": result_payload,

        # ✅ 학생용 요약(라벨 번역본)
        "previous_mistakes_student_friendly": prev_student_friendly,

        # (참고용) 분석 텍스트만 전달
        "previous_judgement_notes": prev_payload,

        "constraints": {
            "max_chars": MAX_FEEDBACK_CHARS,
            "template": "3 headings + 4 bullets (1/1/2)",
            "forbidden": ["정답코드", "완전한 풀이", "코드블록", "백틱", "내부 필드명/라벨"],
        },
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "developer", "content": DEVELOPER_PROMPT},
            {
                "role": "user",
                "content": (
                    "다음 JSON만 근거로, 템플릿 그대로 피드백을 작성해.\n"
                    "- 금지: 내부용어/라벨/코드/백틱/코드블록/링크/추가설명\n"
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

        if reason is not None:
            feedback_text = postprocess(fallback_feedback(req))
            if DEBUG_LOG:
                print("[FALLBACK]", feedback_text)

    except HTTPException as e:
        if DEBUG_LOG:
            print("[GMS ERROR FALLBACK]", e.detail)
        feedback_text = postprocess(fallback_feedback(req))

    _cache_put(ck, feedback_text)
    return {"request_id": req.request_id, "feedback": feedback_text}
