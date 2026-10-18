import json

import pytest

from fde_kit import FakeLLM

VOCAB = ["chest pain", "shortness of breath", "fever", "cough", "rash", "headache"]


def intake_responder(messages, system, tools):
    """Deterministic stand-in for the extraction model. It under-triages chest pain on purpose."""
    text = messages[0]["content"].lower()
    caller = " ".join(l for l in text.splitlines() if l.startswith("caller:"))
    symptoms = [s for s in VOCAB if s in caller]
    if "refill" in caller:
        reason, urgency = "medication refill", "routine"
    else:
        reason, urgency = " and ".join(symptoms[:2]) or "unspecified", "urgent"
    window = ("asap" if "as soon as possible" in caller else "morning" if "morning" in caller
              else "afternoon" if "afternoon" in caller else "any")
    return json.dumps({"reason": reason, "urgency": urgency, "symptoms": symptoms, "callback_window": window})


@pytest.fixture
def llm():
    return FakeLLM(intake_responder)


@pytest.fixture
def calls(cap_data):
    return json.loads((cap_data / "calls.json").read_text(encoding="utf-8"))


@pytest.fixture
def gold(cap_data):
    return json.loads((cap_data / "gold_intakes.json").read_text(encoding="utf-8"))
