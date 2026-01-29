# index.py
import os
import re
import json
import asyncio
from typing import Optional, Literal, Dict, Any

import httpx
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()

# =========================
# Config
# =========================
GMS_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"
MODEL = os.getenv("GMS_MODEL", "gpt-5-mini")

# 서버 간 인증
REQUIRE_SERVER_TOKEN = os.getenv("REQUIRE_SERVER_TOKEN", "0") == "1"
REPORT_SERVER_TOKEN = os.getenv("REPORT_SERVER_TOKEN", "")

HTTP_TIMEOUT = httpx.Timeout(20.0, connect=5.0)
RETRY_MAX = 2
RETRY_BACKOFF_BASE_SEC = 0.6

# 출력 제한
MAX_FEEDBACK_CHARS = 260

app = FastAPI(title="Report Feedback Server", version="1.0.2")


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


class FeedbackRequest(BaseModel):
    request_id: Optional[str] = None
    problem: Problem
    user: User
    code: Code


class FeedbackResponse(BaseModel):
    request_id: Optional[str] = None
    feedback: str


# =========================
# Prompt / Guardrails
# =========================
DEVELOPER_PROMPT = """
Answer in Korean.
You are a friendly teacher coaching a student.

Hard rules:
- Output MUST be 1~2 sentences only.
- Include: (1) one encouragement, (2) one concrete next-step improvement.
- You MAY add at most ONE brief alternative approach hint (keyword-level only).
- Do NOT provide full correct code or a complete solution.
- Do NOT output code blocks or multi-line code.
- Use ONLY the given problem, user info, and student code.
""".strip()


def _dump(obj: BaseModel) -> Dict[str, Any]:
    return obj.model_dump() if hasattr(obj, "model_dump") else obj.dict()


def postprocess(text: str) -> str:
    """공백 정리 + 1~2문장 제한 + 길이 제한"""
    text = re.sub(r"\s+", " ", (text or "")).strip()

    # 2문장 제한(간단 규칙)
    parts = re.split(r"(?<=[.!?])\s+|(?<=[다요]\.)\s+", text)
    text = " ".join([p for p in parts if p][:2]).strip()

    return text[:MAX_FEEDBACK_CHARS].strip()


def violates_policy(text: str) -> bool:
    """교육 서비스용 현실적인 가드레일(과도한 키워드 차단 제거)"""
    if not (text or "").strip():
        return True

    # 코드블록/장문 코드 방지
    if "```" in text:
        return True

    # 과도하게 길면 차단
    if len(text) > MAX_FEEDBACK_CHARS:
        return True

    return False


def tone_hint(user: User, problem: Problem) -> str:
    if user.coding_level <= 2 or user.age <= 14:
        return "아주 친근하고 쉬운 표현으로 단계적으로 설명"
    if problem.difficulty >= 4:
        return "간결하고 정형화된 코칭 톤"
    return "친근하지만 핵심 위주의 코칭 톤"


def fallback_feedback(user: User, problem: Problem) -> str:
    """LLM 출력이 정책 위반/공백일 때 서비스 중단 방지용 기본 피드백"""
    if user.coding_level <= 2 or user.age <= 14:
        return (
            "좋은 시도야! 먼저 입력·출력 형식을 다시 확인하고, "
            "변수를 어디서 선언/사용하는지 한 줄씩 따라가며 점검해보자."
        )
    if problem.difficulty >= 4:
        return (
            "접근은 괜찮아요. 요구 조건과 경계 케이스를 먼저 정리한 뒤, "
            "시간복잡도(제한)를 만족하는 자료구조/방법을 한 번 더 점검해보세요."
        )
    return (
        "좋은 방향이에요! 입력 처리와 예외 케이스를 먼저 확실히 한 다음, "
        "문제를 더 단순한 단계로 나눠서 구현해보면 좋아요."
    )


# =========================
# GMS API Call
# =========================
async def call_gms(payload: dict) -> str:
    api_key = os.getenv("GMS_API_KEY") or os.getenv("GMS_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing GMS_API_KEY (or GMS_KEY)")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        for attempt in range(RETRY_MAX + 1):
            r = await client.post(GMS_URL, headers=headers, json=payload)

            if r.status_code == 200:
                data = r.json()
                try:
                    return data["choices"][0]["message"]["content"]
                except Exception:
                    raise HTTPException(status_code=502, detail=f"Unexpected GMS response: {data}")

            # 재시도 대상
            if r.status_code in (429, 500, 502, 503, 504) and attempt < RETRY_MAX:
                backoff = RETRY_BACKOFF_BASE_SEC * (2 ** attempt)
                await asyncio.sleep(backoff)
                continue

            # 디버그 로그
            print("GMS STATUS:", r.status_code)
            print("GMS BODY:", r.text)

            raise HTTPException(status_code=502, detail=f"GMS error {r.status_code}: {r.text}")

    raise HTTPException(status_code=502, detail="GMS call failed")


# =========================
# Routes
# =========================
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("api/v1/reports/feedback", response_model=FeedbackResponse)
async def feedback(
    req: FeedbackRequest,
    x_report_server_token: Optional[str] = Header(None, alias="X-REPORT-SERVER-TOKEN"),
):
    # (선택) 서버 간 인증
    if REQUIRE_SERVER_TOKEN:
        if x_report_server_token != REPORT_SERVER_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid server token")

    user_payload = {
        "tone_hint": tone_hint(req.user, req.problem),
        "problem": _dump(req.problem),
        "user": _dump(req.user),
        "code": _dump(req.code),
        "output_constraints": {
            "sentences": "1~2",
            "must_include": ["격려 1개", "개선 포인트 1개"],
            "optional_include": ["대안 풀이 힌트 1개(키워드 수준)"],
            "forbidden": ["정답코드", "완전한 풀이", "장문", "코드블록(```)", "멀티라인 코드"],
        },
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "developer", "content": DEVELOPER_PROMPT},
            {
                "role": "user",
                "content": (
                    "아래 JSON을 기반으로 피드백을 작성해줘.\n"
                    "1~2문장, 격려 1개 + 개선 포인트 1개 포함.\n"
                    "대안 풀이가 있다면 키워드 힌트 1개만 제시.\n"
                    "정답 코드나 코드블록은 절대 쓰지 마.\n\n"
                    + json.dumps(user_payload, ensure_ascii=False)
                ),
            },
        ],
        "max_completion_tokens": 120,
    }

    # 1) 1차 생성
    raw = await call_gms(payload)
    feedback_text = postprocess(raw)

    # 2) 정책 위반이면 1회 재생성(더 강한 제약)
    if violates_policy(feedback_text):
        payload["messages"][1]["content"] += (
            "\n\n다시 작성: 1~2문장만. 코드블록/코드/정답/완전풀이 금지. 격려+개선포인트 필수."
        )
        raw2 = await call_gms(payload)
        feedback_text = postprocess(raw2)

    # 3) 그래도 위반이면 서비스용 기본 문구로 대체(502로 터뜨리지 않음)
    if violates_policy(feedback_text):
        feedback_text = fallback_feedback(req.user, req.problem)

    return {"request_id": req.request_id, "feedback": feedback_text}
