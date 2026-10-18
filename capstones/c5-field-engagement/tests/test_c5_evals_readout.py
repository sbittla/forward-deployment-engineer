import dataclasses
import re

import pytest

PACKAGE = "engagement"


def test_evaluate(cap, calls, llm, gold):
    results = cap.run_pipeline(calls, llm)
    m = cap.evaluate(results, gold)
    assert m == {"urgency": 1.0, "symptoms": 1.0, "callback_window": 1.0, "field_accuracy": 1.0,
                 "urgent_recall": 1.0, "calls": 4}
    # without the red-flag override the chest-pain call would have been treated as merely urgent
    weakened = [dataclasses.replace(r, intake={**r.intake, "urgency": "urgent"}) if r.call_id == "C2" else r
                for r in results]
    assert cap.evaluate(weakened, gold)["urgent_recall"] == round(2 / 3, 4)


def test_roi(cap):
    v = cap.roi(calls_per_month=3000, minutes_saved_per_call=4, nurse_hourly_cost=60, monthly_platform_cost=2500,
                one_time_cost=90000)
    assert v == {"nurse_hours_saved_per_month": 200.0, "net_savings_per_month": 9500.0, "payback_months": 9.5}


def test_readout(cap, cap_data, calls, llm, gold):
    charter = cap.parse_notes((cap_data / "discovery_notes.md").read_text(encoding="utf-8"))
    results = cap.run_pipeline(calls, llm)
    md = cap.render_readout(charter, cap.evaluate(results, gold), results, cap.roi(3000, 4, 60, 2500, 90000))
    heads = re.findall(r"^## (.*)$", md, re.M)
    assert heads == ["Executive summary", "What we measured", "Safety", "Voice experience", "Business impact",
                     "Product feedback", "Next steps", "Open questions and assumptions"]
    assert md.startswith("# Lakeside Community Health")
    assert "**GO**" in md and "100% urgent recall" in md and "calls C2" in md
    assert "p95 agent response latency: 2.8 s" in md and "interrupted the agent 1 time" in md
    assert "200.0 nurse hours" in md and "payback in 9.5 months" in md
    assert md.count("Until confirmed, we assume") == 3
