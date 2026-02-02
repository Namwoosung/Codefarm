from typing import Any, Dict, List

# (선택) 금지 단어가 있으면 여기에 유지
BANNED_TERMS = [
    "브루트포스", "최적화", "투포인터", "로직", "정의",
    "시간복잡도", "빅오", "자료구조", "알고리즘"
]

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
    if code_history:
        latest_code = (code_history[-1].get("code") or "")

    developer = f"""
너는 초등~중등 학생에게 코딩 힌트를 주는 튜터다. 반드시 아주 쉬운 한국어만 사용한다.
정답(완성 코드/정답 값)을 직접 주면 안 된다. 학생이 스스로 생각하도록 방향만 준다.

[금지 단어]
{", ".join(BANNED_TERMS)}

[출력 형식]
반드시 JSON 하나만 출력한다(설명/마크다운/코드블록 금지).
스키마:
{{
  "should_send": true/false,
  "feedback_type": "IMMEDIATE|DELAYED|CHECK_IN|ENCOURAGEMENT",
  "hint_style": "SOCRATIC|DIRECTIVE",
  "hint_content": "쉬운 말 힌트(1~4문장)" 또는 "",
  "dedup_reason": "중복일 때만",
  "current_judgement": {{
    "mistake_type": ["..."],
    "reason_short": "..."
  }}
}}
""".strip()

    user = f"""
[학생 정보]
- 나이: {ui.get("age")}
- 코딩 수준(1~5): {ui.get("coding_level")}

[문제 정보]
- 난이도(1~5): {pi.get("difficulty")}
- 설명:
{pi.get("description")}

[시간]
- started_at: {gms_input.get("started_at")}
- observed_at: {gms_input.get("observed_at")}

[학생 질문]
{user_q if user_q else "(질문 없음)"}

[현재 코드]
{latest_code if latest_code else "(아직 코드가 없음)"}

[분류/상태 정보(model2 산출물 포함 가능)]
- current_judgement: {cj}

[이전 판단 목록]
{prev if prev else "(없음)"}

[요청]
- 아주 쉬운 말로 힌트를 1~4문장으로 써줘.
- 이전 힌트와 핵심이 같으면 should_send=false로 하고 hint_content는 ""로 해줘.
- JSON만 출력해줘.
""".strip()

    return [{"role": "developer", "content": developer},
            {"role": "user", "content": user}]
