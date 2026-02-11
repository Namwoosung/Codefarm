from __future__ import annotations

from typing import Any, Dict, List
import re
import json

# =========================
# Terms policy
# =========================

# 일반에서는 너무 메타/전문 용어를 피하고 싶을 때 유지
BANNED_TERMS_GENERAL = [
    "브루트포스", "최적화", "투포인터", "로직", "정의",
    "시간복잡도", "빅오", "자료구조", "알고리즘"
]

# 커리큘럼 모드에서는 초보 설명에 필요한 말(예: 알고리즘/자료구조)을 과도하게 금지하면 설명이 막힘
# => 커리큘럼 모드에서는 불필요한 전문 최적화 용어만 제한
BANNED_TERMS_CURRICULUM = [
    "빅오", "시간복잡도", "최적화"
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
    hints: List[str] = []
    for item in (prev or [])[-limit:]:
        if not isinstance(item, dict):
            continue
        for k in ("hint", "hint_content", "feedback", "message", "assistant_hint"):
            v = item.get(k)
            if isinstance(v, str) and v.strip():
                hints.append(v.strip())
                break

    cleaned: List[str] = []
    for h in hints:
        h = re.sub(r"\s+", " ", h).strip()
        cleaned.append(_trunc(h, 140))
    return cleaned

def _sanitize_for_prompt(obj: Any, max_len: int = 800) -> str:
    try:
        s = str(obj)
    except Exception:
        s = ""
    s = re.sub(r"\s+", " ", s).strip()
    return _trunc(s, max_len)

# =========================
# Curriculum routing (NO problem_type)
# =========================
# ✅ problem_type 관련 내용은 전부 제거
# ✅ algorithm 값이 아래 중 하나면 "커리큘럼 모드"로 간주
_CURRICULUM_ALGO_RAW = {
    "입력과 출력",
    "조건문",
    "반복문",
}

def _is_curriculum_by_algorithm(raw_algo: str) -> bool:
    a = (raw_algo or "").strip()
    if not a:
        return False
    if a in _CURRICULUM_ALGO_RAW:
        return True
    # 괄호/부가설명 포함 케이스 대응: "조건문(기초)" 등
    for key in _CURRICULUM_ALGO_RAW:
        if key and key in a:
            return True
    return False

# =========================
# Question classification (OUTPUT 추가 + "출력"을 DEBUG에서 제거)
# =========================
def _classify_user_question(user_q: str) -> str:
    q = (user_q or "").strip()
    if not q:
        return "NONE"

    output_kw = ["출력", "print", "어떻게 내", "어떻게 출력", "출력 방법"]
    how_kw = ["어떻게", "방법", "풀이", "설명", "알려", "풀어", "작성", "짜", "구현", "어케"]
    concept_kw = ["개념", "뜻", "차이", "왜", "원리", "무슨", "의미", "설명해줘"]
    debug_kw = ["왜 안", "안돼", "오류", "에러", "틀려", "런타임", "테스트", "통과", "틀렸"]

    if any(k in q for k in output_kw):
        return "OUTPUT"
    if any(k in q for k in how_kw):
        return "HOW"
    if any(k in q for k in concept_kw):
        return "CONCEPT"
    if any(k in q for k in debug_kw):
        return "DEBUG"
    return "OTHER"

def _is_output_question(user_q: str) -> bool:
    q = (user_q or "").lower()
    keywords = ["출력", "print", "어떻게 내", "어떻게 출력", "출력 방법"]
    return any(k in q for k in keywords)

# =========================
# Algorithm name mapping (KR/EN -> normalized)
# =========================

_ALGO_SYNONYMS: Dict[str, str] = {
    # ✅ curriculum 대상(입력/출력)
    "입력과 출력": "io",
    "입출력": "io",
    "input/output": "io",

    # condition
    "조건문": "condition",
    "if": "condition",
    "if문": "condition",
    "조건": "condition",

    # loop
    "반복문": "loop",
    "for": "loop",
    "for문": "loop",
    "while": "loop",
    "while문": "loop",
    "반복": "loop",

    # stack
    "stack": "stack",
    "스택": "stack",
    "스택구현": "stack",
    "후입선출": "stack",

    # queue
    "queue": "queue",
    "큐": "queue",
    "선입선출": "queue",
    "덱": "queue",

    # brute force / search
    "완전탐색": "search",
    "탐색": "search",
    "bruteforce": "search",

    # 기타
    "문자열": "string",
    "string": "string",
    "배열": "array",
    "array": "array",
}

def _normalize_algorithm(raw_algo: str) -> str:
    a = (raw_algo or "").strip()
    if not a:
        return "unknown"
    a_low = a.lower()

    if a in _ALGO_SYNONYMS:
        return _ALGO_SYNONYMS[a]
    if a_low in _ALGO_SYNONYMS:
        return _ALGO_SYNONYMS[a_low]

    for k, v in _ALGO_SYNONYMS.items():
        if k and (k in a or k in a_low):
            return v

    return "unknown"

def _algo_display_name(algo_norm: str, raw_algo: str) -> str:
    if algo_norm == "io":
        return "입력과 출력(받고, 그대로/형식 맞춰 내보내기)"
    if algo_norm == "condition":
        return "조건(만약 ~라면) 확인"
    if algo_norm == "loop":
        return "반복(여러 번 같은 일)"
    if algo_norm == "stack":
        return "스택(최근 것부터 꺼내기)"
    if algo_norm == "queue":
        return "큐(먼저 온 것부터 꺼내기)"
    if algo_norm == "search":
        return "하나씩 확인하기"
    if algo_norm == "string":
        return "문자(글자) 다루기"
    if algo_norm == "array":
        return "리스트(줄 세운 값들) 다루기"
    return (raw_algo or "기본 규칙")

# =========================
# Curriculum templates
# =========================
def _curriculum_how_template(algo_norm: str) -> str:
    if algo_norm == "io":
        return (
            "input()으로 받은 값은 한 줄 문자열이야. "
            "map(int, input())처럼 쓰면 글자 하나씩 숫자로 바뀔 수 있어. "
            "공백으로 나눈 뒤 숫자로 바꾸는 과정이 필요한지 확인해봐."
        )
    if algo_norm == "condition":
        return (
            "어떤 경우에 A를, 어떤 경우에 B를 출력해야 하는지 먼저 나눠 적어봐. "
            "값을 조건에 하나씩 넣어보면서 어디에 해당하는지 확인해."
        )
    if algo_norm == "loop":
        return (
            "반복이 몇 번 도는지 먼저 확인해. "
            "작은 예시로 1~2번만 손으로 따라가보면 이해가 쉬워."
        )
    if algo_norm == "stack":
        return (
            "0이 아니면 쌓고, 0이면 하나 되돌린다고 생각해봐. "
            "비어있을 때 0이 나오면 그냥 넘어가야 하는지도 확인해."
        )
    if algo_norm == "queue":
        return (
            "먼저 들어온 것을 먼저 처리해야 해. "
            "작은 예시를 적어서 넣는 순서와 꺼내는 순서를 직접 확인해봐."
        )
    return (
        "입력이 무엇이고 출력이 무엇인지 한 줄로 다시 적어봐. "
        "작은 예시 1개로 과정을 따라가며 확인해."
    )

def _curriculum_output_template_io() -> str:
    return (
        "출력은 print()로 할 수 있어. "
        "리스트를 그대로 출력하면 대괄호([ ])가 같이 나올 수 있어. "
        "값들만 문제에서 원하는 모양(공백/줄바꿈)으로 나오게 하려면 어떻게 출력해야 할지 생각해봐."
    )

def _curriculum_concept_template(algo_disp: str) -> str:
    return (
        f"{algo_disp}에서 가장 중요한 동작이 무엇인지 먼저 떠올려봐. "
        "그 동작이 코드에서 어디에 있는지도 찾아보면 이해가 쉬워."
    )

# =========================
# Main builder
# =========================

def build_gms_messages(gms_input: Dict[str, Any]) -> List[Dict[str, str]]:
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

    prev_hints = _extract_prev_hints(prev, limit=5)
    problem_desc = _trunc(str(pi.get("description") or ""), 900)
    latest_code = _trunc(latest_code, 1200)

    raw_algo = str(pi.get("algorithm") or "").strip()

    # ✅ problem_type 없이 algorithm으로 커리큘럼 모드 판단
    is_curriculum = _is_curriculum_by_algorithm(raw_algo)

    q_type = _classify_user_question(user_q)

    algo_norm = _normalize_algorithm(raw_algo)
    algo_disp = _algo_display_name(algo_norm, raw_algo)

    # =========================
    # ✅ 커리큘럼 템플릿 선택 (출력 질문 최우선)
    # =========================
    curriculum_template = ""
    curriculum_focus = "NONE"  # DEBUG용/설명용 표시만

    if is_curriculum and user_q:
        # 1) 출력 질문이면 "출력"에만 집중
        if algo_norm == "io" and (q_type == "OUTPUT" or _is_output_question(user_q)):
            curriculum_template = _curriculum_output_template_io()
            curriculum_focus = "OUTPUT"

        # 2) HOW 질문(일반 흐름)
        elif q_type == "HOW":
            curriculum_template = _curriculum_how_template(algo_norm)
            curriculum_focus = "HOW"

        # 3) CONCEPT 질문
        elif q_type == "CONCEPT":
            curriculum_template = _curriculum_concept_template(algo_disp)
            curriculum_focus = "CONCEPT"

    banned_terms = BANNED_TERMS_CURRICULUM if is_curriculum else BANNED_TERMS_GENERAL

    # =========================
    # Developer prompt (정책/규칙)
    # =========================
    developer = f"""
너는 초등~중등 학생에게 코딩 힌트를 주는 튜터다. 반드시 아주 쉬운 한국어만 사용한다.
정답(완성 코드/정답 값)을 직접 주면 안 된다. 학생이 스스로 생각하도록 방향만 준다.

[금지 규칙]
- 아래 단어/표현을 출력에 쓰지 마: {", ".join(banned_terms)}
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
  - hint_content는 반드시 null이 아니어야 함
  - dedup_reason는 "" 로 비워

[커리큘럼 규칙 - 최우선(질문 있을 때)]
- is_curriculum=true 이고 학생 질문이 있으면, 일반 규칙보다 아래 규칙을 우선 적용해.
- 커리큘럼 + OUTPUT 질문이면:
  - 출력에만 집중해서 설명해(입력 얘기 최소화).
  - hint_style은 DIRECTIVE를 우선.
- 커리큘럼 + HOW/CONCEPT 질문이면:
  - 사고 순서를 알려주는 방식으로 더 자세히(하지만 정답/완성코드 금지).
  - hint_style은 DIRECTIVE를 우선.

[질문 유효성 규칙]
- 학생 질문이 욕설/무관 질문이면:
  - should_send=true
  - feedback_type=CHECK_IN
  - hint_style=SOCRATIC
  - 문제와 관련된 질문을 하도록 유도하는 말만
  - 정답/코드 힌트는 금지

[중복 방지(질문 없을 때만)]
- should_send=false 조건:
  - 이번 힌트의 "핵심 행동"이 이전 힌트와 거의 같으면 false.
  - should_send=false면 hint_content=null, dedup_reason 필수.

[분류 기준]
- feedback_type:
  - (문제 난이도 > 학생 수준) 이면 IMMEDIATE 우선
  - (문제 난이도 <= 학생 수준) 이면 DELAYED 우선(질문 형태)
  - 코드가 비어있거나 진행이 멈춘 느낌이면 CHECK_IN
  - 잘 하고 있으면 ENCOURAGEMENT
- hint_style:
  - IMMEDIATE면 DIRECTIVE 우선
  - DELAYED면 SOCRATIC 우선
  - 단, 커리큘럼+질문이면 DIRECTIVE 우선

[힌트 작성 규칙]
- 1~4문장, 아주 쉬운 말.
- 학생이 바로 다음으로 할 행동 1~2개만 제시.
- 출력/입력 형식 실수 방지도 포함 가능(YES/NO 철자, 줄바꿈 등).
""".strip()

    # =========================
    # User prompt (컨텍스트)
    # =========================
    user = f"""
[학생 정보]
- 나이: {ui.get("age")}
- 코딩 수준(1~5): {ui.get("coding_level")}

[문제 정보]
- 난이도(1~5): {pi.get("difficulty")}
- algorithm_raw: {raw_algo if raw_algo else "(없음)"}
- algorithm_norm: {algo_norm}
- algorithm_hint: {algo_disp}
- 설명:
{problem_desc}

[커리큘럼/질문 신호]
- is_curriculum: {str(is_curriculum).lower()}
- question_type: {q_type}
- curriculum_focus: {curriculum_focus}

[CURRICULUM_TEMPLATE] (is_curriculum=true & 질문 있을 때 참고)
{curriculum_template if curriculum_template else "(해당 없음)"}

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
