"""utils/prompt_builder.py

Runtime prompt injection for Model-2.

This module is the *online* equivalent of your offline script
`inject_prompt_only_final.py`:

- Adds ONLY a single string field: `prompt`
- Does NOT create any meta fields (prompt_state / prompt_labels / ...)
- Deduplicates labels and enforces the `No_Issue`-only rule
- Adds label-wise anchors for **every** label in `current_judgement.mistake_type`

Design note:
We still compute a coarse `state` (NO_CODE/INPUT/OUTPUT/EDGE/LOGIC/NO_ISSUE)
to add a small state-specific guidance block, because your server design
mentions "state-wise prompts".
"""

from typing import Any, Dict, List

STATE_GUIDANCE_EN: Dict[str, str] = {
    "NO_CODE": "State: NO_CODE. Focus only on the absence/presence of code_history snapshots (and timestamps if present).",
    "INPUT": "State: INPUT. Focus only on reading/parsing/iteration count/read order/missing input handling.",
    "OUTPUT": "State: OUTPUT. Focus only on output formatting (case prefix, spacing, YES/NO tokens, empty-case output).",
    "EDGE": "State: EDGE. Focus only on boundary/empty/zero-case/reset/special-case handling.",
    "LOGIC": "State: LOGIC. Focus only on algorithm/condition/order/target selection/computation logic issues.",
    "NO_ISSUE": "State: NO_ISSUE. Treat the solution as correct; justify briefly using evidence.",
}

# 1) Base prompt for MULTI-LABEL generation (stable)
BASE_PROMPT_MULTI_EN = (
    "You are an assistant that writes a grounded analysis for coding mistake judgements.\n\n"
    "Hard constraints:\n"
    "- Use ONLY evidence from:\n"
    "  (1) code_history (code/diff/trace if present)\n"
    "  (2) current_judgement.mistake_type\n"
    "  (3) problem_information (description and input_description if present)\n"
    "  (4) previous_judgement.mistake_type and judged_at (labels+timestamps only; NOT their analyses)\n"
    "- Do NOT add new labels or issues.\n"
    "- Do NOT give fixes, advice, motivations, or future steps.\n"
    "- Write in English.\n\n"
    "Output format (MULTI-LABEL, ONE LINE):\n"
    "- For EACH label in current_judgement.mistake_type, write exactly: \"<LABEL>: <one short grounded reason>\".\n"
    "- Join label blocks with \"; \" (semicolon + space).\n"
    "- Do NOT use newline.\n"
    "- End with \"[End]\" exactly.\n"
)

STATE_PRIORITY = ["NO_CODE", "INPUT", "OUTPUT", "EDGE", "LOGIC", "NO_ISSUE"]

LABEL_ADDENDUM_EN: Dict[str, str] = {
    "Input_T_MissingOrWrong": "Anchor the explanation on how T is read/used and how the loop count mismatches the described format.",
    "Input_N_ZeroCase": "Anchor the explanation on the N=0 scenario and how the code reads/skips the following line(s).",
    "Input_ReadOrder_Error": "Anchor the explanation on reading order (e.g., reading X before the list or vice versa) compared to input_description.",
    "Input_Parsing_Error": "Anchor the explanation on parsing/splitting/casting steps visible in code_history.",
    "Input_Iteration_Error": "Anchor the explanation on loops iterating the wrong number of inputs/lines/tokens.",
    "Input_MissingOrWrong": "Anchor the explanation on missing reads or reading the wrong variable/token from input.",
    "Input_DataType_Error": "Anchor the explanation on input-side casting/type expectations vs what is read (e.g., str vs int).",

    "Output_Format_MissingCasePrefix": "Anchor the explanation on the absence/misuse of the required case prefix (e.g., #1).",
    "Output_WrongYESNO": "Anchor the explanation on YES/NO string mismatch (case, spelling, or alternative tokens).",
    "Output_Format_Error": "Anchor the explanation on formatting mismatches (spacing/newlines/ordering) visible in print statements.",
    "Output_EmptyCase_HandlingError": "Anchor the explanation on what the code prints when the result is empty/none and how that contradicts the required behavior.",

    "Boundary_Condition_Error": "Anchor the explanation on boundary indices/limits and the specific failing boundary case.",
    "Logic_ZeroCase_Handling_Error": "Anchor the explanation on the zero-case branch/absence of it and how the code behaves there.",
    "Reset_Initialization_Error": "Anchor the explanation on missing/incorrect initialization of flags/containers before use.",
    "Logic_Reset_Per_TestCase_Missing": "Anchor the explanation on state not being reset per test case (variables persist across cases).",
    "Logic_State_Reset_Error": "Anchor the explanation on incorrect reset timing/placement in loops.",
    "Logic_TestCase_Loop_Error": "Anchor the explanation on incorrect test case looping structure.",
    "Queue_Empty_Handling_Error": "Anchor the explanation on pop/dequeue on empty handling.",
    "Queue_Peek_EmptyHandling": "Anchor the explanation on peek/front-check on empty handling.",
    "Stack_Empty_Handling_Error": "Anchor the explanation on pop/peek on empty handling.",

    "Algorithm_BruteForce_NeedsOptimization": "Anchor the explanation on visibly expensive nested loops/approach implied by the latest code_history (without proposing fixes).",
    "Algorithm_CompletelyWrong": "Anchor the explanation on mismatch between the implemented approach and the problem requirement (high-level, grounded to code).",
    "Condition_Bug": "Anchor the explanation on a specific conditional check that does not match the intended logic.",
    "Logic_Iteration_Error": "Anchor the explanation on wrong iteration bounds/step that affects computation (not input reading).",
    "Logic_Order_Handling_Error": "Anchor the explanation on operation order (e.g., update then check vs check then update).",
    "Logic_Queue_Implementation_Inefficient": "Anchor the explanation on an inefficient queue approach visible in code_history (e.g., list pop(0)).",
    "Logic_Result_Handling_Error": "Anchor the explanation on incorrect aggregation/return/printing of computed result (not formatting).",
    "Queue_Order_Error": "Anchor the explanation on wrong queue ordering semantics (front/back behavior).",
    "Stack_Order_Error": "Anchor the explanation on wrong stack ordering semantics (LIFO behavior).",
    "Wrong_Target_Selection": "Anchor the explanation on selecting/comparing against the wrong target variable/value.",
    "DataType_Conversion_Error": "Anchor the explanation on incorrect type conversion during computation (not while reading input).",
    "DataType_String_Operation_Error": "Anchor the explanation on incorrect string operations during computation (split/join/replace/etc.) that affect logic.",
}

META_FIELDS_TO_DROP = [
    "prompt_state",
    "prompt_labels",
    "prompt_label_states",
    "raw_prompt_state",
    "raw_labels",
]

NO_CODE_LABELS = {"NoCode_Persistent", "NoCode_AfterNoIssue", "NoCode_AfterMistake"}

INPUT_LABELS = {
    "Input_DataType_Error",
    "Input_Iteration_Error",
    "Input_MissingOrWrong",
    "Input_N_ZeroCase",
    "Input_Parsing_Error",
    "Input_ReadOrder_Error",
    "Input_T_MissingOrWrong",
}

OUTPUT_LABELS = {
    "Output_Format_Error",
    "Output_Format_MissingCasePrefix",
    "Output_WrongYESNO",
    "Output_EmptyCase_HandlingError",
}

EDGE_LABELS = {
    "Boundary_Condition_Error",
    "Logic_ZeroCase_Handling_Error",
    "Reset_Initialization_Error",
    "Logic_Reset_Per_TestCase_Missing",
    "Logic_State_Reset_Error",
    "Logic_TestCase_Loop_Error",
    "Queue_Empty_Handling_Error",
    "Queue_Peek_EmptyHandling",
    "Stack_Empty_Handling_Error",
}

LOGIC_LABELS = {
    "Algorithm_BruteForce_NeedsOptimization",
    "Algorithm_CompletelyWrong",
    "Condition_Bug",
    "Index_Access_Error",
    "Logic_Iteration_Error",
    "Logic_Order_Handling_Error",
    "Logic_Queue_Implementation_Inefficient",
    "Logic_Result_Handling_Error",
    "Queue_Order_Error",
    "Stack_Order_Error",
    "Wrong_Target_Selection",
    "DataType_Conversion_Error",
    "DataType_String_Operation_Error",
}

def label_to_state(label: str) -> str:
    if label == "No_Issue":
        return "NO_ISSUE"

    if label in NO_CODE_LABELS or label.startswith("NoCode_"):
        return "NO_CODE"

    if label in INPUT_LABELS:
        return "INPUT"

    if label in OUTPUT_LABELS:
        return "OUTPUT"

    if label in EDGE_LABELS:
        return "EDGE"

    if label.startswith("Queue_") or label.startswith("Stack_"):
        if "Empty" in label or "Peek" in label:
            return "EDGE"
        return "LOGIC"

    if label in LOGIC_LABELS:
        return "LOGIC"

    if label.startswith("Logic_"):
        return "LOGIC"

    if label.startswith("Condition_") or label.startswith("Wrong_Target") or label.startswith("Algorithm_"):
        return "LOGIC"

    if label.startswith("DataType_"):
        return "LOGIC"

    return "LOGIC"

def choose_state(mistake_types: List[str]) -> str:
    if not mistake_types:
        return "NO_ISSUE"

    mts = list(dict.fromkeys([m for m in mistake_types if m]))

    # No_Issue는 단독일 때만
    if "No_Issue" in mts and len(mts) > 1:
        mts = [m for m in mts if m != "No_Issue"]

    states = {label_to_state(m) for m in mts}
    for s in STATE_PRIORITY:
        if s in states:
            return s
    return "LOGIC"


def is_known_label(label: str) -> bool:
    return (
        (label == "No_Issue")
        or (label in NO_CODE_LABELS)
        or (label in INPUT_LABELS)
        or (label in OUTPUT_LABELS)
        or (label in EDGE_LABELS)
        or (label in LOGIC_LABELS)
        or label.startswith(
            (
                "NoCode_",
                "Logic_",
                "Condition_",
                "Wrong_Target",
                "Algorithm_",
                "Queue_",
                "Stack_",
                "DataType_",
            )
        )
    )


def dedup_labels(mistake_types: List[str]) -> List[str]:
    mts = [m for m in (mistake_types or []) if isinstance(m, str) and m]
    mts = list(dict.fromkeys(mts))

    # No_Issue only if alone
    if "No_Issue" in mts and len(mts) > 1:
        mts = [m for m in mts if m != "No_Issue"]
    return mts if mts else ["No_Issue"]


def build_prompt_only(mistake_types: List[str]) -> str:
    labels = dedup_labels(mistake_types)
    state = choose_state(labels)

    parts: List[str] = [BASE_PROMPT_MULTI_EN]
    parts.append(STATE_GUIDANCE_EN.get(state, "State: LOGIC."))
    parts.append("")
    parts.append("Label-specific anchors (apply each anchor ONLY to its label):")

    for lb in labels:
        anchor = LABEL_ADDENDUM_EN.get(lb)
        if anchor:
            parts.append(f"- {lb}: {anchor}")
        else:
            # keep generic fallback to prevent anchor hallucination
            parts.append(f"- {lb}: Focus on evidence cues relevant to this label only.")

    return "\n".join(parts).rstrip() + "\n"

def sanitize_payload_for_model2(req_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure we never forward stale meta fields to Model-2."""
    out = dict(req_payload)
    for k in META_FIELDS_TO_DROP:
        out.pop(k, None)
    return out


def build_prompt(model2_input_raw: Dict[str, Any]) -> str:
    cj = model2_input_raw.get("current_judgement", {}) or {}
    mts: List[str] = cj.get("mistake_type", []) or []
    return build_prompt_only(mts)
