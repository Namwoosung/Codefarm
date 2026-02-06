# models/model1.py  (4bit quantized load, 붙여넣기 버전)
from __future__ import annotations

import os
import json
import threading
from typing import Any, Dict, List, Tuple

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    BitsAndBytesConfig,
)
from torch.nn.functional import sigmoid

from utils.labels import dedup_labels

# ============================================================
# Model1 (Label classifier)
# - Default: load in 4bit on GPU to coexist with model2 on A100 20GB
# - Avoid huge RAM usage by preventing accidental CPU offload
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/models/"
DEFAULT_MODEL_DIR = os.path.join(BASE_DIR, "label_model")
MODEL_DIR = os.getenv("LABEL_MODEL_DIR", DEFAULT_MODEL_DIR).strip()

# Inference params
DEFAULT_THRESHOLD = float(os.getenv("MODEL1_THRESHOLD", "0.3"))
DEFAULT_TOPK = int(os.getenv("MODEL1_TOPK", "5"))
MAX_LEN = int(os.getenv("MODEL1_MAX_LEN", "1024"))

# Device
CUDA_DEVICE_INDEX = int(os.getenv("CUDA_DEVICE_INDEX", "0"))

# Quantization flags (4bit default ON)
MODEL1_LOAD_IN_4BIT = os.getenv("MODEL1_LOAD_IN_4BIT", "1") == "1"
MODEL1_LOAD_IN_8BIT = os.getenv("MODEL1_LOAD_IN_8BIT", "0") == "1"  # fallback option

# (중요) CPU offload 허용 여부
# - 기본 0: offload 방지(=RAM 폭증 방지) / GPU에 강제 로드
# - 1: 정말 GPU가 부족할 때만 "auto+max_memory"로 CPU offload 허용
MODEL1_ALLOW_CPU_OFFLOAD = os.getenv("MODEL1_ALLOW_CPU_OFFLOAD", "0") == "1"

# (선택) offload 허용 시에만 사용
MODEL1_MAX_MEMORY = os.getenv("MODEL1_MAX_MEMORY", "11GiB").strip()  # 예: "11GiB"
MODEL1_CPU_MAX_MEMORY = os.getenv("MODEL1_CPU_MAX_MEMORY", "64GiB").strip()

# Label space (must match training)
BASE_LABELS: List[str] = [
    "Algorithm_BruteForce_NeedsOptimization", "Algorithm_CompletelyWrong",
    "Boundary_Condition_Error", "Condition_Bug", "DataType_Conversion_Error",
    "DataType_String_Operation_Error", "Index_Access_Error",
    "Input_DataType_Error", "Input_Iteration_Error", "Input_MissingOrWrong",
    "Input_N_ZeroCase", "Input_Parsing_Error", "Input_ReadOrder_Error",
    "Input_T_MissingOrWrong", "Logic_Iteration_Error", "Logic_Order_Handling_Error",
    "Logic_Queue_Implementation_Inefficient", "Logic_Reset_Per_TestCase_Missing",
    "Logic_Result_Handling_Error", "Logic_State_Reset_Error",
    "Logic_TestCase_Loop_Error", "Logic_ZeroCase_Handling_Error",
    "NoCode_AfterMistake", "NoCode_AfterNoIssue", "NoCode_Persistent",
    "No_Issue", "Output_EmptyCase_HandlingError", "Output_Format_Error",
    "Output_Format_MissingCasePrefix", "Output_WrongYESNO",
    "Queue_Empty_Handling_Error", "Queue_Order_Error",
    "Queue_Peek_EmptyHandling", "Reset_Initialization_Error",
    "Stack_Empty_Handling_Error", "Stack_Order_Error",
    "Wrong_Target_Selection",
]
ID2LABEL = {i: l for i, l in enumerate(BASE_LABELS)}

_tokenizer = None
_model = None
_LOAD_LOCK = threading.Lock()


def _primary_device(model) -> torch.device:
    # quantized models may not have simple .device
    hf_map = getattr(model, "hf_device_map", None)
    if isinstance(hf_map, dict):
        for _, d in hf_map.items():
            if isinstance(d, str) and d.startswith("cuda"):
                return torch.device(d)
    return torch.device(f"cuda:{CUDA_DEVICE_INDEX}" if torch.cuda.is_available() else "cpu")


def _build_bnb_config() -> BitsAndBytesConfig | None:
    if not torch.cuda.is_available():
        return None

    # 4bit 우선
    if MODEL1_LOAD_IN_4BIT:
        # A100 권장: bfloat16 compute
        compute_dtype = torch.bfloat16
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=compute_dtype,
        )

    # 8bit 모드(선택)
    if MODEL1_LOAD_IN_8BIT:
        return BitsAndBytesConfig(load_in_8bit=True)

    return None


def _load_once():
    global _tokenizer, _model
    if _tokenizer is not None and _model is not None:
        return

    with _LOAD_LOCK:
        if _tokenizer is not None and _model is not None:
            return

        if not os.path.isdir(MODEL_DIR):
            raise FileNotFoundError(f"label_model directory not found: {MODEL_DIR}")
        if not os.path.exists(os.path.join(MODEL_DIR, "config.json")):
            raise FileNotFoundError(f"{MODEL_DIR} missing config.json")

        _tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)

        kwargs: Dict[str, Any] = {
            "local_files_only": True,
            "low_cpu_mem_usage": True,
        }

        if torch.cuda.is_available():
            bnb = _build_bnb_config()
            if bnb is not None:
                kwargs["quantization_config"] = bnb

            # ✅ 기본은 GPU 고정 로드 (CPU offload 방지)
            if not MODEL1_ALLOW_CPU_OFFLOAD:
                kwargs["device_map"] = {"": f"cuda:{CUDA_DEVICE_INDEX}"}
            else:
                # ✅ offload 허용 시에만 auto+max_memory 사용
                kwargs["device_map"] = "auto"
                if MODEL1_MAX_MEMORY:
                    kwargs["max_memory"] = {
                        CUDA_DEVICE_INDEX: MODEL1_MAX_MEMORY,
                        "cpu": MODEL1_CPU_MAX_MEMORY,
                    }

        _model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR, **kwargs)
        _model.eval()

        # 로그 (운영 디버깅용)
        print(f"[Model1] loaded from: {MODEL_DIR}", flush=True)
        if torch.cuda.is_available():
            print(f"[Model1] cuda:{CUDA_DEVICE_INDEX}", flush=True)
            print(
                "[Model1] quant:",
                ("4bit" if MODEL1_LOAD_IN_4BIT else ("8bit" if MODEL1_LOAD_IN_8BIT else "fp16/bf16")),
                "allow_cpu_offload:",
                MODEL1_ALLOW_CPU_OFFLOAD,
                "max_memory:",
                (MODEL1_MAX_MEMORY if MODEL1_ALLOW_CPU_OFFLOAD and MODEL1_MAX_MEMORY else "OFF"),
                flush=True,
            )
            hf_map = getattr(_model, "hf_device_map", None)
            if isinstance(hf_map, dict):
                # cpu가 섞이면 RAM 사용 커질 수 있음
                cpu_cnt = sum(1 for v in hf_map.values() if v == "cpu")
                cuda_cnt = sum(1 for v in hf_map.values() if isinstance(v, str) and v.startswith("cuda"))
                print(f"[Model1] hf_device_map stats: cuda={cuda_cnt} cpu={cpu_cnt}", flush=True)


def _payload_to_text(payload: Dict[str, Any]) -> str:
    """
    ✅ 현재 5분 구간 코드만 들어오므로 code_history를 모두 포함해도 됨.
    단, 코드 길이만 컷해서 입력 폭주를 방지.
    """
    ui = payload.get("user_information", {}) or {}
    pi = payload.get("problem_information", {}) or {}
    prev = payload.get("previous_judgement", []) or []
    code_hist = payload.get("code_history", []) or []

    hist = []
    for it in code_hist:
        if not isinstance(it, dict):
            continue
        code = it.get("code")
        if not isinstance(code, str):
            continue
        code = code.strip()
        if len(code) > 2000:
            code = code[:2000] + "…"
        hist.append({"timestamp": it.get("timestamp"), "code": code})

    prev_labels = []
    for it in (prev or [])[-3:]:
        if isinstance(it, dict):
            mts = it.get("mistake_type") or []
            if isinstance(mts, list):
                prev_labels.append([x for x in mts if isinstance(x, str)])

    desc = (pi.get("description") or "")
    if len(desc) > 700:
        desc = desc[:700] + "…"

    doc = {
        "age": ui.get("age"),
        "level": ui.get("coding_level"),
        "problem_id": pi.get("problem_id"),
        "difficulty": pi.get("difficulty"),
        "algorithm": pi.get("algorithm"),
        "description": desc,
        "user_question": (payload.get("user_question") or "")[:200],
        "previous_labels": prev_labels,
        "code_history": hist,
    }
    return json.dumps(doc, ensure_ascii=False)


@torch.inference_mode()
def predict_payload(
    payload: Dict[str, Any],
    *,
    topk: int = DEFAULT_TOPK,
    threshold: float = DEFAULT_THRESHOLD,
) -> Tuple[List[Tuple[str, float]], List[Tuple[str, float]]]:
    _load_once()

    text = _payload_to_text(payload)
    inputs = _tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_LEN,
        padding=True,  # dynamic padding (batch=1)
    )

    device = _primary_device(_model)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    logits = _model(**inputs).logits.squeeze(0)
    probs = sigmoid(logits)

    pred_labels = [(ID2LABEL[i], probs[i].item()) for i in range(len(probs)) if probs[i] >= threshold]
    pred_labels.sort(key=lambda x: x[1], reverse=True)

    # No_Issue 제거 규칙
    if len(pred_labels) > 1:
        pred_labels = [(l, p) for l, p in pred_labels if l != "No_Issue"]

    k = min(max(topk, 1), len(probs))
    topk_idx = torch.topk(probs, k).indices
    topk_labels = [(ID2LABEL[i.item()], probs[i].item()) for i in topk_idx]

    return pred_labels, topk_labels


def run_model1(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    ✅ sync 유지 (app.py에서 run_in_threadpool로 실행 가능)
    """
    preds, _ = predict_payload(payload)
    mistake_types = dedup_labels([label for label, _ in preds])
    return {"mistake_type": mistake_types}
