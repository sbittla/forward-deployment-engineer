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
    raise NotImplementedError


def extract_intake(llm, transcript: str, max_attempts: int = 2) -> dict:
    raise NotImplementedError


def triage(intake: dict, transcript: str) -> tuple[dict, list[str]]:
    """Escalate to emergency when any red flag appears, whatever the model said. Never downgrade."""
    raise NotImplementedError
