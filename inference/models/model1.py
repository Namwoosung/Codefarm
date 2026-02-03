# models/model1.py
from __future__ import annotations

import os
import json
from typing import Any, Dict, List, Tuple

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import sigmoid

from utils.labels import dedup_labels


# ============================================================
# Model1 (Label classifier) - single HF model in ./label_model
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/models/"
DEFAULT_MODEL_DIR = os.path.join(BASE_DIR, "label_model")

# ✅ 단일 모델 디렉터리
MODEL_DIR = os.getenv("LABEL_MODEL_DIR", DEFAULT_MODEL_DIR).strip()

# Inference params
DEFAULT_THRESHOLD = float(os.getenv("MODEL1_THRESHOLD", "0.5"))
DEFAULT_TOPK = int(os.getenv("MODEL1_TOPK", "5"))
MAX_LEN = int(os.getenv("MODEL1_MAX_LEN", "1024"))

# Label space (must match training)
BASE_LABELS: List[str] = [
    "Algorithm_BruteForce_NeedsOptimization","Algorithm_CompletelyWrong",
    "Boundary_Condition_Error","Condition_Bug","DataType_Conversion_Error",
    "DataType_String_Operation_Error","Index_Access_Error",
    "Input_DataType_Error","Input_Iteration_Error","Input_MissingOrWrong",
    "Input_N_ZeroCase","Input_Parsing_Error","Input_ReadOrder_Error",
    "Input_T_MissingOrWrong","Logic_Iteration_Error","Logic_Order_Handling_Error",
    "Logic_Queue_Implementation_Inefficient","Logic_Reset_Per_TestCase_Missing",
    "Logic_Result_Handling_Error","Logic_State_Reset_Error",
    "Logic_TestCase_Loop_Error","Logic_ZeroCase_Handling_Error",
    "NoCode_AfterMistake","NoCode_AfterNoIssue","NoCode_Persistent",
    "No_Issue","Output_EmptyCase_HandlingError","Output_Format_Error",
    "Output_Format_MissingCasePrefix","Output_WrongYESNO",
    "Queue_Empty_Handling_Error","Queue_Order_Error",
    "Queue_Peek_EmptyHandling","Reset_Initialization_Error",
    "Stack_Empty_Handling_Error","Stack_Order_Error",
    "Wrong_Target_Selection"
]

ID2LABEL = {i: l for i, l in enumerate(BASE_LABELS)}

_tokenizer = None
_model = None


def _primary_device(model) -> torch.device:
    dev = getattr(model, "device", None)
    if isinstance(dev, torch.device):
        return dev

    hf_map = getattr(model, "hf_device_map", None)
    if isinstance(hf_map, dict):
        for _, d in hf_map.items():
            if isinstance(d, str) and d not in ("cpu", "disk", "meta"):
                return torch.device(d)

    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _load_once():
    global _tokenizer, _model
    if _tokenizer is not None and _model is not None:
        return

    if not os.path.isdir(MODEL_DIR):
        raise FileNotFoundError(f"label_model directory not found: {MODEL_DIR}")

    if not os.path.exists(os.path.join(MODEL_DIR, "config.json")):
        raise FileNotFoundError(
            f"{MODEL_DIR} does not look like a HF model directory (missing config.json)"
        )

    _tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
    _model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_DIR,
        device_map="auto",
        local_files_only=True,
    )
    _model.eval()

    print(f"[Model1] loaded label model from: {MODEL_DIR}", flush=True)


def _payload_to_text(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)


@torch.no_grad()
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
        padding="max_length",
    )

    device = _primary_device(_model)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    logits = _model(**inputs).logits.squeeze(0)
    probs = sigmoid(logits)

    pred_labels = [
        (ID2LABEL[i], probs[i].item())
        for i in range(len(probs))
        if probs[i] >= threshold
    ]
    pred_labels.sort(key=lambda x: x[1], reverse=True)

    # No_Issue 제거 규칙
    if len(pred_labels) > 1:
        pred_labels = [(l, p) for l, p in pred_labels if l != "No_Issue"]

    k = min(max(topk, 1), len(probs))
    topk_idx = torch.topk(probs, k).indices
    topk_labels = [(ID2LABEL[i.item()], probs[i].item()) for i in topk_idx]

    return pred_labels, topk_labels


async def run_model1(payload: Dict[str, Any]) -> Dict[str, Any]:
    preds, _ = predict_payload(payload)

    mistake_types = [label for label, _ in preds]
    mistake_types = dedup_labels(mistake_types)

    return {"mistake_type": mistake_types}
