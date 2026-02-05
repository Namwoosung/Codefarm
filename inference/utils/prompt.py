from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
import re
import json

# (선택) 금지 단어가 있으면 여기에 유지
BANNED_TERMS = [
    "브루트포스", "최적화", "투포인터", "로직", "정의",
    "시간복잡도", "빅오", "자료구조", "알고리즘"
]

_JSON_ONLY_REMINDER = (
    "반드시 JSON 하나만 출력해. "
    "설명/마크다운/코드블록/앞뒤 문장/주석을 절대 붙이지 마. "
    "JSON은 반드시 큰따옴표(\")를 써."
)

def _trunc(s: str, n: int) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[:n] + "…"

def _extract_prev_hints(prev: List[Dict[str, Any]], limit: int = 5) -> List[str]:
    """
    previous_judgement에서 'hint' 또는 유사 필드를 최대한 뽑아낸다.
    - 구조가 팀마다 다른 경우를 대비한 방어형 추출
    """
    hints: List[str] = []
    for item in (prev or [])[-limit:]:
        if not isinstance(item, dict):
            continue

        # 후보 키들(팀 데이터에 맞춰 확장 가능)
        for k in ("hint", "hint_content", "feedback", "message", "assistant_hint"):
            v = item.get(k)
            if isinstance(v, str) and v.strip():
                hints.append(v.strip())
                break

    # 너무 길면 비교가 어려우니 정제
    cleaned: List[str] = []
    for h in hints:
        h = re.sub(r"\s+", " ", h).strip()
        cleaned.append(_trunc(h, 140))
    return cleaned

def _sanitize_for_prompt(obj: Any, max_len: int = 800) -> str:
    """
    프롬프트 주입/폭주 방지: JSON dump 대신 짧은 문자열로 안전 요약
    """
    try:
        s = str(obj)
    except Exception:
        s = ""
    s = re.sub(r"\s+", " ", s).strip()
    return _trunc(s, max_len)

def build_gms_messages(gms_input: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    model2 output(gms_input) -> gms chat.completions messages 변환

    gms_input 예:
      {
        started_at, observed_at, language,
        user_question(optional),
        user_information, problem_information,
        code_history, previous_judgement,
        current_judgement(optional) ...
      }
    """
    user_q = (gms_input.get("user_question") or "").strip()

    ui = gms_input.get("user_information", {}) or {}
    pi = gms_input.get("problem_information", {}) or {}
    code_history = gms_input.get("code_history", []) or []
    prev = gms_input.get("previous_judgement", []) or []
    cj = gms_input.get("current_judgement", {}) or {}

    latest_code = ""
    if isinstance(code_history, list) and code_history:
        last = code_history[-1] or {}
        if isinstance(last, dict):
            latest_code = (last.get("code") or "")

    # ✅ 중복 판단용: 이전 힌트 텍스트만 추출
    prev_hints = _extract_prev_hints(prev, limit=5)

    # ✅ 문제/코드 길이 폭주 방지(필요시 값 조정)
    problem_desc = _trunc(str(pi.get("description") or ""), 900)
    latest_code = _trunc(latest_code, 1200)

    # =========================
    # Developer prompt (강제 규칙)
    # =========================
    developer = f"""
너는 초등~중등 학생에게 코딩 힌트를 주는 튜터다. 반드시 아주 쉬운 한국어만 사용한다.
정답(완성 코드/정답 값)을 직접 주면 안 된다. 학생이 스스로 생각하도록 방향만 준다.

[금지 규칙]
- 아래 단어/표현을 출력에 쓰지 마: {", ".join(BANNED_TERMS)}
- "정답 코드", "완전한 풀이", "정답 값"을 주지 마.
- 코드블록(```), 백틱(`), 마크다운을 쓰지 마.
- 시스템/모델/프롬프트 같은 말을 쓰지 마.

[출력 형식]
{_JSON_ONLY_REMINDER}
반드시 다음 스키마를 만족하는 JSON 하나만 출력해(추가 키 금지).

키 순서까지 지켜:
1) should_send
2) feedback_type
3) hint_style
4) hint_content
5) dedup_reason
6) current_judgement

스키마:
{{
  "should_send": true/false,
  "feedback_type": "IMMEDIATE" | "DELAYED" | "CHECK_IN" | "ENCOURAGEMENT",
  "hint_style": "SOCRATIC" | "DIRECTIVE",
  "hint_content": "쉬운 말 힌트(1~4문장)" 또는 null,
  "dedup_reason": "중복일 때만 짧게(1문장)" 또는 "",
  "current_judgement": {{
    "mistake_type": ["..."],
    "reason_short": "아주 짧게(1문장)"
  }}
}}

[결정 규칙 - 최우선]
- 학생 질문(user_question)이 비어있지 않으면:
  - should_send는 반드시 true
  - 중복 판단을 절대 하지 마(이전 힌트와 비슷해도 무조건 새 힌트 제공)
  - hint_content는 반드시 null이 아니어야 함(즉, 실제 힌트를 써야 함)
  - dedup_reason는 "" 로 비워

[질문 유효성 규칙]
- 학생 질문(user_question)이 아래에 해당하면 "무관 질문"으로 본다:
  - 욕설, 비속어, 공격적인 표현
  - 욕설 예시: 바보, 멍청, 욕, 비하 표현
  - 문제/코드/입력/출력과 관계없는 내용
  - 감정 표현만 있고 질문이 아닌 경우

- 무관 질문일 때 처리 방식:
  - should_send = true
  - feedback_type = CHECK_IN
  - hint_style = SOCRATIC
  - hint_content에는 문제와 관련된 질문을 하도록 유도하는 말만 쓴다
  - 정답이나 코드 힌트는 절대 주지 않는다
  
[무관 질문 응답 규칙]
- 욕설이나 무관 질문에는 약간의 훈육이 필요하고, 학생이 다시 집중하도록 유도해야 한다
- hint_content 예시: "문제와 관련 없는 질문이에요. 지금은 문제 해결에 집중해 볼까요?"

[결정 규칙 - 중복 방지(단, 학생 질문이 없을 때만)]
- should_send=false 조건:
  - 이번에 만들 힌트의 "핵심 행동"이 "이전 힌트 목록" 중 하나와 거의 같으면 false.
  - '핵심 행동' 예: (입력 읽기 순서 점검 / 변수 초기화 위치 점검 / 반복문에서 찾으면 바로 멈추기 / YES/NO 출력 조건 점검 등)
  - 단어만 살짝 바꾼 정도로 의미가 같으면 중복으로 본다.
  - should_send=false면:
    - hint_content는 반드시 null
    - dedup_reason는 반드시 채워(짧게 1문장)

[분류 기준]
- feedback_type:
  - (문제 난이도 > 학생 수준) 이면 IMMEDIATE 우선
  - (문제 난이도 <= 학생 수준) 이면 DELAYED 우선(질문 형태)
  - 코드가 비어있거나 진행이 멈춘 느낌이면 CHECK_IN
  - 정답/통과 상태거나 잘 하고 있으면 ENCOURAGEMENT
- hint_style:
  - IMMEDIATE면 DIRECTIVE 우선(하지만 정답 제시 금지)
  - DELAYED면 SOCRATIC 우선(질문 형태)

[힌트 작성 규칙]
- 1~4문장, 아주 쉬운 말.
- 학생이 바로 다음으로 할 행동 1~2개만 제시.
- 출력/입력 형식 주의가 필요하면 "한 줄 더 출력되는지/YES NO 철자/케이스 표기" 같은 실수 방지 포인트를 포함할 수 있음.
""".strip()

    # =========================
    # User prompt (증거/상황)
    # =========================
    user = f"""
[학생 정보]
- 나이: {ui.get("age")}
- 코딩 수준(1~5): {ui.get("coding_level")}

[문제 정보]
- 난이도(1~5): {pi.get("difficulty")}
- 설명:
{problem_desc}

[시간]
- started_at: {gms_input.get("started_at")}
- observed_at: {gms_input.get("observed_at")}

[학생 질문(user_question)]
{user_q if user_q else "(질문 없음)"}

[현재 코드]
{latest_code if latest_code else "(아직 코드가 없음)"}

[분류/상태 정보(model2 산출물)]
- current_judgement: {_sanitize_for_prompt(cj, 500)}

[이전 힌트 목록(중복 판단용)]
{json.dumps(prev_hints, ensure_ascii=False) if prev_hints else "[]"}
""".strip()

    return [
        {"role": "developer", "content": developer},
        {"role": "user", "content": user},
    ]