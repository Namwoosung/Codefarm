from __future__ import annotations

from typing import Any, Dict, List
import re
import json

# =========================
# Terms policy
# =========================

# 일반(비커리큘럼)에서는 너무 메타/전문 용어를 피하고 싶을 때 유지
BANNED_TERMS_GENERAL = [
    "브루트포스", "최적화", "투포인터", "로직", "정의",
    "시간복잡도", "빅오", "자료구조", "알고리즘"
]

# 커리큘럼에서는 초보 설명에 필요한 말(예: 알고리즘/자료구조)을 과도하게 금지하면 설명이 막힘
# => 커리큘럼 모드에서는 금지어를 더 좁게 잡는다(정답/완성코드 금지는 별도 강제)
BANNED_TERMS_CURRICULUM = [
    "빅오", "시간복잡도", "최적화"  # 초보 단계에서 불필요한 전문 최적화 용어만 제한
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

def _is_curriculum_problem(pi: Dict[str, Any]) -> bool:
    pt = (pi.get("problem_type") or pi.get("type") or "").strip().lower()
    return pt == "curriculum"

def _classify_user_question(user_q: str) -> str:
    q = (user_q or "").strip()
    if not q:
        return "NONE"

    how_kw = ["어떻게", "방법", "풀이", "설명", "알려", "풀어", "작성", "짜", "구현", "어케"]
    concept_kw = ["개념", "뜻", "차이", "왜", "원리", "무슨", "의미", "설명해줘"]
    debug_kw = ["왜 안", "안돼", "오류", "에러", "틀려", "런타임", "출력", "입력", "테스트", "통과", "틀렸"]

    if any(k in q for k in how_kw):
        return "HOW"
    if any(k in q for k in concept_kw):
        return "CONCEPT"
    if any(k in q for k in debug_kw):
        return "DEBUG"
    return "OTHER"

# =========================
# Algorithm name mapping (KR/EN -> normalized)
# =========================

_ALGO_SYNONYMS: Dict[str, str] = {
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
    "덱": "queue",  # 덱/큐로 분류(설명은 큐 기반으로)

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
    """
    한국어/영어/혼합 algorithm 값을 정규화해서 템플릿 선택에 사용.
    """
    a = (raw_algo or "").strip()
    if not a:
        return "unknown"
    a_low = a.lower()

    # 정확 매핑 우선
    if a in _ALGO_SYNONYMS:
        return _ALGO_SYNONYMS[a]
    if a_low in _ALGO_SYNONYMS:
        return _ALGO_SYNONYMS[a_low]

    # 포함 매칭(예: "조건문(기초)" 같은 형태)
    for k, v in _ALGO_SYNONYMS.items():
        if k and (k in a or k in a_low):
            return v

    return "unknown"

def _algo_display_name(algo_norm: str, raw_algo: str) -> str:
    """
    모델에게 보여줄 쉬운 이름(학생용).
    """
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
# Curriculum HOW templates (short, stable)
# =========================

def _curriculum_how_template(algo_norm: str) -> str:
    """
    커리큘럼 + HOW 질문일 때, 힌트를 안정적으로 만들기 위한 짧은 템플릿.
    - 1~4문장 내에서 끝나도록 설계
    - 정답/완성코드 금지
    """
    if algo_norm == "condition":
        return (
            "먼저 어떤 경우에 A를, 어떤 경우에 B를 출력해야 하는지 조건을 2~3개로 나눠 적어봐. "
            "그 다음 점수/값을 조건에 넣어보면서 어느 구간에 들어가는지 확인해. "
            "마지막에 출력 글자(대소문자, 줄바꿈)가 문제랑 똑같은지 확인해."
        )
    if algo_norm == "loop":
        return (
            "반복이 몇 번 도는지(입력으로 N이나 T가 있는지) 먼저 확인해. "
            "반복 안에서 해야 할 일을 한 줄로 정리한 뒤, 작은 예시로 1~2번만 손으로 따라가봐. "
            "반복이 끝날 때 값이 초기화되어야 하는지도 점검해."
        )
    if algo_norm == "stack":
        return (
            "값을 하나씩 보면서 0이 아니면 '쌓기', 0이면 '하나 되돌리기(빼기)'라고 생각해봐. "
            "쌓아둔 게 비어있을 때 0이 나오면 그냥 넘어가야 하는지도 확인해. "
            "끝나고 남은 것들을 합치거나 개수를 세면 돼."
        )
    if algo_norm == "queue":
        return (
            "먼저 들어온 것을 먼저 처리해야 하니, '앞에서 꺼내기' 순서를 지키는지 생각해봐. "
            "값을 넣는 순서와 꺼내는 순서를 작은 예시로 직접 적어보면 실수가 줄어. "
            "비어있을 때 꺼내려고 하는 상황이 없는지도 확인해."
        )
    # unknown / 기타
    return (
        "먼저 입력이 무엇인지, 출력이 무엇인지 한 줄로 다시 적어봐. "
        "작은 예시 1개로 손으로 과정을 따라가며 중간 값이 어떻게 바뀌는지 확인해. "
        "마지막 출력 형식이 문제 설명과 같은지도 점검해."
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

    is_curriculum = _is_curriculum_problem(pi)
    q_type = _classify_user_question(user_q)

    raw_algo = str(pi.get("algorithm") or "").strip()
    algo_norm = _normalize_algorithm(raw_algo)
    algo_disp = _algo_display_name(algo_norm, raw_algo)

    # 커리큘럼+HOW면 템플릿을 "강제 참고"로 제공(출력 안정화)
    curriculum_how_template = ""
    if is_curriculum and q_type == "HOW":
        curriculum_how_template = _curriculum_how_template(algo_norm)

    banned_terms = BANNED_TERMS_CURRICULUM if is_curriculum else BANNED_TERMS_GENERAL

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

[커리큘럼 특별 규칙 - 매우 중요]
- is_curriculum=true 이고, 학생 질문이 있고(q_type이 HOW/CONCEPT 중 하나)라면:
  - 학생이 처음 배우는 중일 가능성이 높다.
  - 힌트는 더 자세히(하지만 정답/완성코드는 금지) 설명해야 한다.
  - hint_style은 DIRECTIVE를 우선으로 선택한다.
  - {algo_disp} 관점에서 "어떤 순서로 생각하면 되는지"를 알려준다.
  - 가능하면 간단한 메서드/동작을 쉬운 말로 설명한다(예: 넣기/빼기/앞에서 꺼내기/조건 비교).

[HOW 질문 템플릿 고정 규칙]
- is_curriculum=true AND q_type=HOW 이면:
  - 아래 [HOW_TEMPLATE]의 흐름을 최대한 그대로 사용해.
  - 문장 수는 2~4문장으로 줄여.
  - 정답/완성코드/정답 값은 절대 주지 마.

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
  - 단, 커리큘럼+HOW/CONCEPT 질문이면 DIRECTIVE 우선

[힌트 작성 규칙]
- 1~4문장, 아주 쉬운 말.
- 학생이 바로 다음으로 할 행동 1~2개만 제시.
- 출력/입력 형식 실수 방지도 포함 가능(YES/NO 철자, 줄바꿈 등).
""".strip()

    user = f"""
[학생 정보]
- 나이: {ui.get("age")}
- 코딩 수준(1~5): {ui.get("coding_level")}

[문제 정보]
- 난이도(1~5): {pi.get("difficulty")}
- problem_type: {pi.get("problem_type") or "(없음)"}
- algorithm_raw: {raw_algo if raw_algo else "(없음)"}
- algorithm_norm: {algo_norm}
- algorithm_hint: {algo_disp}
- 설명:
{problem_desc}

[커리큘럼/질문 신호]
- is_curriculum: {str(is_curriculum).lower()}
- question_type: {q_type}

[HOW_TEMPLATE] (is_curriculum=true & q_type=HOW일 때만 참고)
{curriculum_how_template if curriculum_how_template else "(해당 없음)"}

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
