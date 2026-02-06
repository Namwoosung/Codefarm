# models/model2.py
# ------------------------------------------------------------
# Model2 (text generation) module (NO FastAPI here).
# - Loads base LLM + LoRA adapter (QLoRA 4-bit)
# - Generates analysis "<LABEL>: <reason>; ... [End]"
# - Returns dict consumable by GMS prompt builder
# ------------------------------------------------------------

from __future__ import annotations

import os
import json
import re
import asyncio
import threading
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import torch
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

from utils.labels import dedup_labels, map_label_alias

END_TEXT = "[End]"

# ============================================================
# Path base (CWD-safe)
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]  # .../AI_server


def _abs(p: str) -> str:
    if not p:
        return ""
    pp = Path(p)
    if pp.is_absolute():
        return str(pp)
    return str((BASE_DIR / pp).resolve())


def _resolve_fold_dir(root: str, fold: int) -> str:
    root_p = Path(_abs(root))
    if not root_p.exists():
        raise FileNotFoundError(f"MODEL2_ADAPTER_ROOT not found: {root_p}")
    candidates = [root_p / f"fold_{fold}", root_p / f"fold{fold}"]
    for c in candidates:
        if c.is_dir():
            return str(c.resolve())
    raise FileNotFoundError(
        f"Adapter fold directory not found under {root_p}. "
        f"Tried: {', '.join(str(x) for x in candidates)}"
    )


# ============================================================
# Env / Config
# ============================================================

ADAPTER_DIR_ENV = os.getenv("MODEL2_ADAPTER_DIR", "").strip()
ADAPTER_ROOT = os.getenv("MODEL2_ADAPTER_ROOT", "./models/text_model/").strip()
ADAPTER_FOLD = int(os.getenv("MODEL2_ADAPTER_FOLD", "5"))

BASE_MODEL = os.getenv("MODEL2_BASE_MODEL", "").strip()  # optional

MAX_LEN = int(os.getenv("MODEL2_MAX_LEN", "1536"))
MAX_NEW_TOKENS = int(os.getenv("MODEL2_MAX_NEW_TOKENS", "120"))

DO_SAMPLE = os.getenv("MODEL2_DO_SAMPLE", "0") == "1"
TEMPERATURE = float(os.getenv("MODEL2_TEMPERATURE", "0.0"))
TOP_P = float(os.getenv("MODEL2_TOP_P", "1.0"))
REPETITION_PENALTY = float(os.getenv("MODEL2_REPETITION_PENALTY", "1.10"))
NO_REPEAT_NGRAM_SIZE = int(os.getenv("MODEL2_NO_REPEAT_NGRAM_SIZE", "4"))

BAN_HANGUL = os.getenv("BAN_HANGUL", "0") == "1"
BAN_HANGUL_MAX_VOCAB_SCAN = int(os.getenv("BAN_HANGUL_MAX_VOCAB_SCAN", "50000"))  # 기본 제한(전체스캔 금지)
FORCE_ENGLISH_REMINDER = os.getenv("FORCE_ENGLISH_REMINDER", "1") == "1"

# GPU headroom / device
CUDA_DEVICE_INDEX = int(os.getenv("CUDA_DEVICE_INDEX", "0"))
MODEL2_MAX_MEMORY = os.getenv("MODEL2_MAX_MEMORY", "").strip()  # 예: "8GiB" (비우면 미사용)

# ✅ generate 동시성 제한(프로세스 내 1개)
# _GEN_LOCK = asyncio.Lock()
_GEN_SEM = asyncio.Semaphore(2)

# ✅ load_model_once 스레드 안전
_LOAD_LOCK = threading.Lock()

if ADAPTER_DIR_ENV:
    ADAPTER_DIR = _abs(ADAPTER_DIR_ENV)
else:
    ADAPTER_DIR = _resolve_fold_dir(ADAPTER_ROOT, ADAPTER_FOLD)


# ============================================================
# Helpers for building input text (training-style)
# ============================================================

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
        mts = dedup_labels(it.get("mistake_type", []))
        rows.append({"judged_at": judged_at, "mistake_type": mts})
    return rows


def build_input_text(rec: Dict[str, Any]) -> str:
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

    mts = dedup_labels(cj.get("mistake_type", []))

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
    text = _enforce_one_line(text)
    if END_TEXT in text:
        text = text.split(END_TEXT, 1)[0].strip()

    parts = [p.strip() for p in text.split(";") if p.strip()]
    out: List[Tuple[str, str]] = []
    for p in parts:
        m = re.match(r"^([A-Za-z0-9_]+)\s*:\s*(.+)$", p)
        if not m:
            continue
        lb = map_label_alias(m.group(1).strip())
        reason = m.group(2).strip()
        if reason:
            out.append((lb, reason))
    return out


def force_only_expected_labels(raw_output: str, expected_labels: List[str]) -> str:
    expected_labels = [x for x in dedup_labels(expected_labels) if x]
    expected_set = set(expected_labels)

    body = _enforce_one_line(raw_output or "")
    if "OUTPUT:" in body:
        body = body.split("OUTPUT:", 1)[1].strip()
    if END_TEXT in body:
        body = body.split(END_TEXT, 1)[0].strip()

    parsed = _parse_blocks(body)

    keep_map: Dict[str, str] = {}
    for lb, reason in parsed:
        if lb in expected_set and lb not in keep_map:
            keep_map[lb] = reason

    leftover = re.sub(r"\b[A-Za-z0-9_]+\s*:\s*", "", body).strip()
    if not leftover:
        leftover = "A grounded reason could not be extracted from the generation, but the evidence indicates this label."

    blocks = []
    for lb in expected_labels:
        reason = keep_map.get(lb) or leftover
        blocks.append(f"{lb}: {_enforce_one_line(reason)}")

    out = "; ".join(blocks).strip()
    out = _enforce_one_line(out)
    out = out.split(END_TEXT, 1)[0].strip() + f" {END_TEXT}"
    return out


# ============================================================
# Stopping criteria
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
    out: List[List[int]] = []
    for v in variants:
        ids = tokenizer.encode(v, add_special_tokens=False)
        if ids:
            out.append(ids)
    uniq: List[List[int]] = []
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
    vocab_size = getattr(tokenizer, "vocab_size", None)
    if vocab_size is None:
        return None

    limit = BAN_HANGUL_MAX_VOCAB_SCAN if BAN_HANGUL_MAX_VOCAB_SCAN > 0 else vocab_size
    limit = min(limit, vocab_size)

    banned: List[int] = []
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
    return torch.device(f"cuda:{CUDA_DEVICE_INDEX}" if torch.cuda.is_available() else "cpu")


def load_model_once() -> None:
    global _tokenizer, _model, _stopping, _logits_processors
    if _tokenizer is not None and _model is not None:
        return

    with _LOAD_LOCK:
        if _tokenizer is not None and _model is not None:
            return

        if not ADAPTER_DIR or not os.path.isdir(ADAPTER_DIR):
            raise FileNotFoundError(f"MODEL2_ADAPTER_DIR not found: {ADAPTER_DIR}")

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

        kwargs = dict(
            quantization_config=bnb_config,
            device_map={"": f"cuda:{CUDA_DEVICE_INDEX}"} if torch.cuda.is_available() else None,
            low_cpu_mem_usage=True,
        )
        if torch.cuda.is_available() and MODEL2_MAX_MEMORY:
            # max_memory를 쓰면 device_map을 auto로 바꿔야 동작하는 경우가 많음
            kwargs["device_map"] = "auto"
            kwargs["max_memory"] = {CUDA_DEVICE_INDEX: MODEL2_MAX_MEMORY, "cpu": "64GiB"}

        base_model = AutoModelForCausalLM.from_pretrained(base, **kwargs)
        base_model.eval()

        _model = PeftModel.from_pretrained(base_model, ADAPTER_DIR)
        _model.eval()

        stop_variants = build_stop_variants(_tokenizer)
        sc_list = [StopOnTokenSequence(ids) for ids in stop_variants]
        _stopping = StoppingCriteriaList(sc_list) if sc_list else None

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
        print("[MODEL2] max_memory:", ({CUDA_DEVICE_INDEX: MODEL2_MAX_MEMORY} if (torch.cuda.is_available() and MODEL2_MAX_MEMORY) else "OFF"))
        print("[MODEL2] ban_hangul:", BAN_HANGUL, "logits_proc:", (len(lp) if lp else 0))
        print("[MODEL2] stop_variants:", stop_variants)


@torch.inference_mode()
def generate_analysis(payload: Dict[str, Any]) -> str:
    load_model_once()
    assert _tokenizer is not None and _model is not None

    cj = payload.get("current_judgement", {}) or {}
    if not isinstance(cj, dict):
        cj = {}

    expected_labels = dedup_labels(cj.get("mistake_type", []))
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
    if "OUTPUT:" in decoded:
        decoded = decoded.split("OUTPUT:", 1)[1].strip()

    decoded = _cut_first_end(decoded)
    decoded = _enforce_one_line(decoded)

    return force_only_expected_labels(decoded, expected_labels)


async def run_model2(model2_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run model2 and return gms_input dict.
    - current_judgement.analysis = model2 analysis
    - generate 동시성: 프로세스 내 1개로 제한
    """
    async with _GEN_SEM:
        analysis_pred = await asyncio.to_thread(generate_analysis, model2_input)

    out = dict(model2_input)
    cj = out.get("current_judgement", {}) or {}
    if not isinstance(cj, dict):
        cj = {}
    cj = dict(cj)

    cj["mistake_type"] = dedup_labels(cj.get("mistake_type", []))
    cj["analysis"] = analysis_pred
    out["current_judgement"] = cj

    out["model2_analysis"] = analysis_pred
    return out
