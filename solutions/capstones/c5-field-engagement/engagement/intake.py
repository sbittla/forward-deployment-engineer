"""Structured intake extraction with schema validation and a deterministic red-flag safety net."""
import json
import re

URGENCY = ("emergency", "urgent", "routine")
WINDOWS = ("asap", "morning", "afternoon", "evening", "any")
RED_FLAGS = ("chest pain", "shortness of breath", "difficulty breathing", "stroke", "slurred speech",
             "suicidal", "severe bleeding", "unconscious")

SYSTEM = (
    "Extract a nurse-callback intake from a de-identified after-hours call transcript. Reply with only JSON: "
    '{"reason": str, "urgency": "emergency"|"urgent"|"routine", "symptoms": [str], '
    '"callback_window": "asap"|"morning"|"afternoon"|"evening"|"any"}. '
    "Use lower-case symptom names. Do not give medical advice."
)


def _validate(obj) -> list[str]:
    errs = []
    if not isinstance(obj, dict):
        return ["reply must be a JSON object"]
    if not isinstance(obj.get("reason"), str) or not obj["reason"].strip():
        errs.append("reason must be a non-empty string")
    if obj.get("urgency") not in URGENCY:
        errs.append(f"urgency must be one of {URGENCY}")
    if not isinstance(obj.get("symptoms"), list) or not all(isinstance(s, str) for s in obj["symptoms"]):
        errs.append("symptoms must be a list of strings")
    if obj.get("callback_window") not in WINDOWS:
        errs.append(f"callback_window must be one of {WINDOWS}")
    return errs


def extract_intake(llm, transcript: str, max_attempts: int = 2) -> dict:
    messages = [{"role": "user", "content": transcript}]
    errs = []
    for _ in range(max_attempts):
        reply = llm.complete(list(messages), system=SYSTEM, max_tokens=400).text
        m = re.search(r"\{.*\}", reply, re.S)
        try:
            obj = json.loads(m.group(0)) if m else None
        except json.JSONDecodeError:
            obj = None
        errs = _validate(obj) if obj is not None else ["reply was not JSON"]
        if not errs:
            obj["symptoms"] = sorted({s.strip().lower() for s in obj["symptoms"]})
            return obj
        messages += [{"role": "assistant", "content": reply},
                     {"role": "user", "content": "Invalid intake: " + "; ".join(errs) + ". Return corrected JSON."}]
    raise ValueError("intake extraction failed: " + "; ".join(errs))


def triage(intake: dict, transcript: str) -> tuple[dict, list[str]]:
    """Escalate to emergency when any red flag appears, whatever the model said. Never downgrade."""
    text = (transcript + " " + " ".join(intake.get("symptoms", []))).lower()
    flags = [f for f in RED_FLAGS if f in text]
    if flags:
        intake = {**intake, "urgency": "emergency", "callback_window": "asap"}
    return intake, flags
