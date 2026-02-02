import json
from typing import Any, Dict, List

from utils.constants import BANNED_TERMS

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
