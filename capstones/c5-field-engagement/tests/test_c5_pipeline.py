import importlib
import json

import pytest

from fde_kit import FakeLLM

PACKAGE = "engagement"


def test_pipeline_end_to_end(cap, calls, llm):
    results = cap.run_pipeline(calls, llm)
    by = {r.call_id: r for r in results}
    assert by["C2"].intake["urgency"] == "emergency" and by["C2"].red_flags == ["chest pain", "shortness of breath"]
    assert by["C3"].intake == {"reason": "medication refill", "urgency": "routine", "symptoms": [],
                               "callback_window": "afternoon"}
    assert by["C1"].phi_tokens >= 4 and by["C1"].voice["barge_ins"] == 0
    sent = " ".join(m["content"] for c in llm.calls for m in c["messages"])
    for leak in ("Maria", "Carter", "88231", "04/02/1981", "415-555-0100", "wei.zhang@example.com", "773"):
        assert leak not in sent


def test_guard_blocks_phi(cap):
    pipeline = importlib.import_module("engagement.pipeline")
    guarded = pipeline._GuardedLLM(FakeLLM(["{}"]), ["Maria Lopez"])
    with pytest.raises(cap.PHILeak):
        guarded.complete([{"role": "user", "content": "Caller: this is Maria, DOB 04/02/1981"}])


def test_extraction_repair_and_failure(cap):
    good = {"reason": "cough", "urgency": "urgent", "symptoms": ["Cough", "cough"], "callback_window": "any"}
    llm = FakeLLM(['{"reason": "cough", "urgency": "very bad"}', json.dumps(good)])
    out = cap.extract_intake(llm, "Caller: cough")
    assert out["symptoms"] == ["cough"] and len(llm.calls) == 2
    assert "urgency must be one of" in llm.calls[1]["messages"][-1]["content"]
    with pytest.raises(ValueError):
        cap.extract_intake(FakeLLM(["nope", "still nope"]), "x")


def test_triage_never_downgrades(cap):
    intake = {"reason": "x", "urgency": "routine", "symptoms": [], "callback_window": "morning"}
    out, flags = cap.triage(intake, "Caller: my father has slurred speech")
    assert out["urgency"] == "emergency" and out["callback_window"] == "asap" and flags == ["slurred speech"]
    same, flags = cap.triage({**intake, "urgency": "urgent"}, "Caller: sore throat")
    assert same["urgency"] == "urgent" and flags == []
