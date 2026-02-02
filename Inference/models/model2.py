# model2_text_server.py
# ------------------------------------------------------------
# Model2 (text generation) inference server for production
# - Load base LLM + LoRA adapter (QLoRA 4-bit)
# - Build input text (prompt + evidence JSON + OUTPUT:)
# - model.generate
# - Force-format to "<LABEL>: <reason>; ... [End]" (always)
# - Optional Hangul suppression logits processor
# ------------------------------------------------------------

import os
import json
import re
from typing import Any, Dict, List, Tuple, Optional

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    StoppingCriteria,
    StoppingCriteriaList,
    LogitsProcessor,
    LogitsProcessorList,
)

from peft import PeftModel, PeftConfig


# ============================================================
# Env / Config
# ============================================================

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8002"))

# If you trained folds, point this to the adapter you want to serve.
# e.g. ./cv_outputs_analysis_qlora_v3/fold_5
ADAPTER_DIR = os.getenv("MODEL2_ADAPTER_DIR", "").strip()

# Base model can be inferred from adapter config, but allow override.
BASE_MODEL = os.getenv("MODEL2_BASE_MODEL", "").strip()  # optional

MAX_LEN = int(os.getenv("MODEL2_MAX_LEN", "1536"))
MAX_NEW_TOKENS = int(os.getenv("MODEL2_MAX_NEW_TOKENS", "120"))

DO_SAMPLE = os.getenv("MODEL2_DO_SAMPLE", "0") == "1"
TEMPERATURE = float(os.getenv("MODEL2_TEMPERATURE", "0.0"))
TOP_P = float(os.getenv("MODEL2_TOP_P", "1.0"))
REPETITION_PENALTY = float(os.getenv("MODEL2_REPETITION_PENALTY", "1.10"))
NO_REPEAT_NGRAM_SIZE = int(os.getenv("MODEL2_NO_REPEAT_NGRAM_SIZE", "4"))

BAN_HANGUL = os.getenv("BAN_HANGUL", "0") == "1"
BAN_HANGUL_MAX_VOCAB_SCAN = int(os.getenv("BAN_HANGUL_MAX_VOCAB_SCAN", "0"))  # 0이면 전체 스캔
FORCE_ENGLISH_REMINDER = os.getenv("FORCE_ENGLISH_REMINDER", "1") == "1"

END_TEXT = "[End]"
IO_BUFFER = 1024 * 1024

MODEL2_ADAPTER_DIR = './cv_outputs_analysis_qlora_v3/fold_5'
MODEL2_MAX_NEW_TOKENS=120
BAN_HANGUL=1


# ============================================================
# Label alias / typo tolerance (formatter + eval 공통 스타일)
# ============================================================

LABEL_ALIAS_RULES: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"^Input_ReadOrder_.*$", re.IGNORECASE), "Input_ReadOrder_Error"),
    (re.compile(r"^Input_ReadOrder_Mismatch$", re.IGNORECASE), "Input_ReadOrder_Error"),
    (re.compile(r"^Input_Iterations?_Error$", re.IGNORECASE), "Input_Iteration_Error"),
    (re.compile(r"^Input_T_Iteration_Error$", re.IGNORECASE), "Input_Iteration_Error"),
    (re.compile(r"^Output_Format_MissingCasePrefix$", re.IGNORECASE), "Output_Format_MissingCasePrefix"),
    (re.compile(r"^Output_Format_.*$", re.IGNORECASE), "Output_Format_Error"),
    (re.compile(r"^Output_Format_Error$", re.IGNORECASE), "Output_Format_Error"),
    # 흔한 철자/케이스 변형
    (re.compile(r"^Input_N_Zero_case$", re.IGNORECASE), "Input_N_ZeroCase"),
]

def safe_list(x) -> List[Any]:
    return x if isinstance(x, list) else ([] if x is None else [x])

def normalize_mistake_types(mts: Any) -> List[str]:
    mts = safe_list(mts)
    out = []
    for m in mts:
        if isinstance(m, str) and m.strip():
            out.append(m.strip())
    out = list(dict.fromkeys(out))
    if "No_Issue" in out and len(out) > 1:
        out = [x for x in out if x != "No_Issue"]
    return out if out else ["No_Issue"]

def _map_label_alias(lb: str) -> str:
    if not lb:
        return lb
    for pat, canon in LABEL_ALIAS_RULES:
        if pat.match(lb):
            return canon
    return lb

def last_code_from_history(code_history: Any) -> str:
    if not isinstance(code_history, list) or not code_history:
        return ""
    for it in reversed(code_history):
        if isinstance(it, dict) and isinstance(it.get("code"), str) and it["code"].strip():
            return it["code"].strip()
    return ""

def prev_label_summary(prev: Any, max_items: int = 6) -> List[Dict[str, Any]]:
    if not isinstance(prev, list) or not prev:
        return []
    rows = []
    for it in prev[-max_items:]:
        if not isinstance(it, dict):
            continue
        judged_at = it.get("judged_at", "")
        mts = it.get("mistake_type", [])
        mts = [m for m in safe_list(mts) if isinstance(m, str) and m.strip()]
        rows.append({"judged_at": judged_at, "mistake_type": mts})
    return rows

def build_input_text(rec: Dict[str, Any]) -> str:
    """
    Training-style:
      prompt + "\n\nEVIDENCE (JSON):\n" + evidence_json + "\n\nOUTPUT:\n"
    + optional strong reminder (English-only, format-only)
    """
    prompt = rec.get("prompt", "")
    if not isinstance(prompt, str):
        prompt = ""

    pi = rec.get("problem_information", {}) or {}
    if not isinstance(pi, dict):
        pi = {}

    cj = rec.get("current_judgement", {}) or {}
    if not isinstance(cj, dict):
        cj = {}

    prev = rec.get("previous_judgement", []) or []
    code_hist = rec.get("code_history", []) or []
    latest_code = last_code_from_history(code_hist)

    mts = normalize_mistake_types(cj.get("mistake_type", []))

    evidence = {
        "problem_information": {
            "algorithm": pi.get("algorithm", ""),
            "difficulty": pi.get("difficulty", ""),
            "problem_id": pi.get("problem_id", ""),
            "description": pi.get("description", ""),
            "input_description": pi.get("input_description", ""),
        },
        "current_judgement": {"mistake_type": mts},
        "previous_judgement": prev_label_summary(prev),
        "latest_code": latest_code,
    }

    reminder = ""
    if FORCE_ENGLISH_REMINDER:
        reminder = (
            "REMINDER:\n"
            "- Write in English ONLY.\n"
            "- Output MUST be one line.\n"
            "- For EACH label in current_judgement.mistake_type, output exactly: \"<LABEL>: <one short grounded reason>\".\n"
            "- Join blocks with \"; \".\n"
            "- End with \"[End]\" exactly.\n\n"
        )

    text = (
        prompt.rstrip()
        + "\n\n"
        + "EVIDENCE (JSON):\n"
        + json.dumps(evidence, ensure_ascii=False)
        + "\n\n"
        + reminder
        + "OUTPUT:\n"
    )
    return text


# ============================================================
# Post-processing: force label blocks format
# ============================================================

def _enforce_one_line(text: str) -> str:
    text = (text or "").replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def _cut_first_end(text: str) -> str:
    if not isinstance(text, str):
        return ""
    idx = text.find(END_TEXT)
    if idx >= 0:
        return text[: idx + len(END_TEXT)].strip()
    return text.strip()

def _parse_blocks(text: str) -> List[Tuple[str, str]]:
    """
    Parse "<LABEL>: reason" blocks separated by ';'
    Returns list of (label, reason)
    """
    text = _enforce_one_line(text)
    # remove trailing [End] noise if present
    if END_TEXT in text:
        text = text.split(END_TEXT, 1)[0].strip()

    parts = [p.strip() for p in text.split(";") if p.strip()]
    out = []
    for p in parts:
        m = re.match(r"^([A-Za-z0-9_]+)\s*:\s*(.+)$", p)
        if not m:
            continue
        lb = _map_label_alias(m.group(1).strip())
        reason = m.group(2).strip()
        if reason:
            out.append((lb, reason))
    return out

def force_only_expected_labels(raw_output: str, expected_labels: List[str]) -> str:
    """
    HARD GUARANTEE:
    - Output contains ONLY expected labels
    - Output includes a block for each expected label
    - Ends exactly once with [End]
    """
    expected_labels = [x for x in normalize_mistake_types(expected_labels) if x]
    expected_set = set(expected_labels)

    body = _enforce_one_line(raw_output or "")
    if "OUTPUT:" in body:
        body = body.split("OUTPUT:", 1)[1].strip()
    if END_TEXT in body:
        body = body.split(END_TEXT, 1)[0].strip()

    parsed = _parse_blocks(body)

    keep_map: Dict[str, str] = {}
    for lb, reason in parsed:
        lb = _map_label_alias(lb)
        if lb in expected_set and lb not in keep_map:
            keep_map[lb] = reason

    leftover = body
    leftover = re.sub(r"\b[A-Za-z0-9_]+\s*:\s*", "", leftover).strip()
    if not leftover:
        # 최소 placeholder (서비스 안전성 우선)
        leftover = "A grounded reason could not be extracted from the generation, but the evidence indicates this label."

    blocks = []
    for lb in expected_labels:
        reason = keep_map.get(lb) or leftover
        reason = _enforce_one_line(reason)
        blocks.append(f"{lb}: {reason}")

    out = "; ".join(blocks).strip()
    out = _enforce_one_line(out)
    out = out + f" {END_TEXT}"
    # ensure exactly once
    out = out.split(END_TEXT, 1)[0].strip() + f" {END_TEXT}"
    return out


# ============================================================
# Stopping criteria: stop on token sequence variants
# ============================================================

class StopOnTokenSequence(StoppingCriteria):
    def __init__(self, stop_ids: List[int]):
        super().__init__()
        self.stop_ids = stop_ids

    def __call__(self, input_ids, scores, **kwargs):
        if input_ids is None or input_ids.shape[1] < len(self.stop_ids):
            return False
        tail = input_ids[0, -len(self.stop_ids):].tolist()
        return tail == self.stop_ids


def build_stop_variants(tokenizer) -> List[List[int]]:
    variants = ["[End]", " [End]", "\n[End]", "\n [End]"]
    out = []
    for v in variants:
        ids = tokenizer.encode(v, add_special_tokens=False)
        if ids:
            out.append(ids)
    # de-dup
    uniq = []
    seen = set()
    for ids in out:
        t = tuple(ids)
        if t not in seen:
            seen.add(t)
            uniq.append(ids)
    return uniq


# ============================================================
# Optional: Hangul suppression logits processor
# ============================================================

_HANGUL_RE = re.compile(r"[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7A3]")

class BanTokenIdsProcessor(LogitsProcessor):
    def __init__(self, banned_ids: List[int]):
        self.banned_ids = banned_ids

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        if self.banned_ids:
            scores[:, self.banned_ids] = -float("inf")
        return scores

def build_hangul_ban_processor(tokenizer) -> Optional[BanTokenIdsProcessor]:
    vocab_size = tokenizer.vocab_size if hasattr(tokenizer, "vocab_size") else None
    if vocab_size is None:
        return None

    limit = BAN_HANGUL_MAX_VOCAB_SCAN if BAN_HANGUL_MAX_VOCAB_SCAN > 0 else vocab_size
    limit = min(limit, vocab_size)

    banned = []
    for tid in range(limit):
        s = tokenizer.decode([tid], skip_special_tokens=False)
        if _HANGUL_RE.search(s or ""):
            banned.append(tid)

    if not banned:
        return None
    return BanTokenIdsProcessor(banned)


# ============================================================
# Model loading (once)
# ============================================================

_tokenizer = None
_model = None
_stopping = None
_logits_processors = None

def _primary_device(model) -> torch.device:
    dev = getattr(model, "device", None)
    if isinstance(dev, torch.device):
        return dev
    hf_map = getattr(model, "hf_device_map", None)
    if isinstance(hf_map, dict) and hf_map:
        for _, d in hf_map.items():
            if isinstance(d, str) and d not in ("cpu", "disk", "meta"):
                return torch.device(d)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model_once():
    global _tokenizer, _model, _stopping, _logits_processors

    if _tokenizer is not None and _model is not None:
        return

    if not ADAPTER_DIR or not os.path.isdir(ADAPTER_DIR):
        raise FileNotFoundError(f"MODEL2_ADAPTER_DIR not found or empty: {ADAPTER_DIR}")

    # Infer base model from adapter if not given
    base = BASE_MODEL
    if not base:
        peft_cfg = PeftConfig.from_pretrained(ADAPTER_DIR)
        base = peft_cfg.base_model_name_or_path

    compute_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=compute_dtype,
    )

    _tokenizer = AutoTokenizer.from_pretrained(base, use_fast=True)
    if _tokenizer.pad_token is None:
        _tokenizer.pad_token = _tokenizer.eos_token
    _tokenizer.padding_side = "right"

    base_model = AutoModelForCausalLM.from_pretrained(
        base,
        quantization_config=bnb_config,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    base_model.eval()

    _model = PeftModel.from_pretrained(base_model, ADAPTER_DIR)
    _model.eval()

    # stopping criteria variants
    stop_variants = build_stop_variants(_tokenizer)
    sc_list = []
    for ids in stop_variants:
        sc_list.append(StopOnTokenSequence(ids))
    _stopping = StoppingCriteriaList(sc_list) if sc_list else None

    # logits processors
    lp = LogitsProcessorList()
    if BAN_HANGUL:
        proc = build_hangul_ban_processor(_tokenizer)
        if proc is not None:
            lp.append(proc)
    _logits_processors = lp if len(lp) > 0 else None

    dev = _primary_device(_model)
    print("[MODEL2] base:", base)
    print("[MODEL2] adapter:", ADAPTER_DIR)
    print("[MODEL2] device:", dev)
    print("[MODEL2] ban_hangul:", BAN_HANGUL, "logits_proc:", (len(lp) if lp else 0))
    print("[MODEL2] stop_variants:", stop_variants)


@torch.inference_mode()
def generate_analysis(payload: Dict[str, Any]) -> str:
    load_model_once()
    assert _tokenizer is not None and _model is not None

    cj = payload.get("current_judgement", {}) or {}
    if not isinstance(cj, dict):
        cj = {}

    expected_labels = normalize_mistake_types(cj.get("mistake_type", []))

    text = build_input_text(payload)
    inputs = _tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_LEN,
    )

    dev = _primary_device(_model)
    inputs = {k: v.to(dev) for k, v in inputs.items()}

    gen_ids = _model.generate(
        **inputs,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=DO_SAMPLE,
        temperature=TEMPERATURE if DO_SAMPLE else None,
        top_p=TOP_P if DO_SAMPLE else None,

        repetition_penalty=REPETITION_PENALTY,
        no_repeat_ngram_size=NO_REPEAT_NGRAM_SIZE,

        use_cache=True,
        eos_token_id=_tokenizer.eos_token_id,
        pad_token_id=_tokenizer.pad_token_id,
        stopping_criteria=_stopping,
        logits_processor=_logits_processors,
    )

    decoded = _tokenizer.decode(gen_ids[0], skip_special_tokens=True)

    # keep only after OUTPUT:
    if "OUTPUT:" in decoded:
        decoded = decoded.split("OUTPUT:", 1)[1].strip()

    decoded = _cut_first_end(decoded)
    decoded = _enforce_one_line(decoded)

    final = force_only_expected_labels(decoded, expected_labels)
    return final


# ============================================================
# FastAPI schema / app
# ============================================================

class PredictRequest(BaseModel):
    payload: Dict[str, Any]

class PredictResponse(BaseModel):
    analysis_pred: str

app = FastAPI(title="CodeFarm Model2 Text Inference Server", version="1.0.0")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        pred = generate_analysis(req.payload)
        return PredictResponse(analysis_pred=pred)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
