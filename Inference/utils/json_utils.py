import json
from typing import Any, Dict, List

BANNED_TERMS = [
    "브루트포스", "최적화", "투포인터", "로직", "정의",
    "시간복잡도", "빅오", "자료구조", "알고리즘"
]

def parse_json(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    try:
        return json.loads(text)
    except Exception:
        s = text.find("{")
        e = text.rfind("}")
        if s != -1 and e != -1 and e > s:
            return json.loads(text[s:e+1])
        raise

def has_banned(obj: Dict[str, Any]) -> bool:
    s = json.dumps(obj, ensure_ascii=False)
    return any(t in s for t in BANNED_TERMS)
