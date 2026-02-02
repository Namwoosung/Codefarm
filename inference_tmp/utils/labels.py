# utils/labels.py
# Centralized label utilities (dedup/normalize/alias/known-label checks)

from __future__ import annotations
from typing import Any, Dict, List, Tuple
import re

# --- Alias / typo tolerance ---
LABEL_ALIAS_RULES: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"^Input_ReadOrder_.*$", re.IGNORECASE), "Input_ReadOrder_Error"),
    (re.compile(r"^Input_ReadOrder_Mismatch$", re.IGNORECASE), "Input_ReadOrder_Error"),
    (re.compile(r"^Input_Iterations?_Error$", re.IGNORECASE), "Input_Iteration_Error"),
    (re.compile(r"^Input_T_Iteration_Error$", re.IGNORECASE), "Input_Iteration_Error"),
    (re.compile(r"^Output_Format_MissingCasePrefix$", re.IGNORECASE), "Output_Format_MissingCasePrefix"),
    (re.compile(r"^Output_Format_.*$", re.IGNORECASE), "Output_Format_Error"),
    (re.compile(r"^Output_Format_Error$", re.IGNORECASE), "Output_Format_Error"),
    (re.compile(r"^Input_N_Zero_case$", re.IGNORECASE), "Input_N_ZeroCase"),
]

def safe_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else ([] if x is None else [x])

def map_label_alias(lb: str) -> str:
    if not lb:
        return lb
    for pat, canon in LABEL_ALIAS_RULES:
        if pat.match(lb):
            return canon
    return lb

def dedup_labels(mistake_types: Any) -> List[str]:
    """Deduplicate labels, remove empties, enforce No_Issue-only rule."""
    mts = safe_list(mistake_types)
    out: List[str] = []
    for m in mts:
        if isinstance(m, str) and m.strip():
            out.append(map_label_alias(m.strip()))
    out = list(dict.fromkeys(out))
    # No_Issue only if alone
    if "No_Issue" in out and len(out) > 1:
        out = [x for x in out if x != "No_Issue"]
    return out if out else ["No_Issue"]

# Known label sets (for validation/logging only)
NO_CODE_LABELS = {"NoCode_Persistent", "NoCode_AfterNoIssue", "NoCode_AfterMistake"}

INPUT_LABELS = {
    "Input_DataType_Error", "Input_Iteration_Error", "Input_MissingOrWrong",
    "Input_N_ZeroCase", "Input_Parsing_Error", "Input_ReadOrder_Error", "Input_T_MissingOrWrong",
}

OUTPUT_LABELS = {
    "Output_Format_Error", "Output_Format_MissingCasePrefix",
    "Output_WrongYESNO", "Output_EmptyCase_HandlingError",
}

EDGE_LABELS = {
    "Boundary_Condition_Error", "Logic_ZeroCase_Handling_Error", "Reset_Initialization_Error",
    "Logic_Reset_Per_TestCase_Missing", "Logic_State_Reset_Error", "Logic_TestCase_Loop_Error",
    "Queue_Empty_Handling_Error", "Queue_Peek_EmptyHandling", "Stack_Empty_Handling_Error",
}

LOGIC_LABELS = {
    "Algorithm_BruteForce_NeedsOptimization", "Algorithm_CompletelyWrong",
    "Condition_Bug", "Index_Access_Error", "Logic_Iteration_Error",
    "Logic_Order_Handling_Error", "Logic_Queue_Implementation_Inefficient",
    "Logic_Result_Handling_Error", "Queue_Order_Error", "Stack_Order_Error",
    "Wrong_Target_Selection", "DataType_Conversion_Error", "DataType_String_Operation_Error",
}

def is_known_label(label: str) -> bool:
    if not isinstance(label, str) or not label:
        return False
    return (
        (label == "No_Issue")
        or (label in NO_CODE_LABELS)
        or (label in INPUT_LABELS)
        or (label in OUTPUT_LABELS)
        or (label in EDGE_LABELS)
        or (label in LOGIC_LABELS)
        or label.startswith((
            "NoCode_", "Logic_", "Condition_", "Wrong_Target",
            "Algorithm_", "Queue_", "Stack_", "DataType_"
        ))
    )
