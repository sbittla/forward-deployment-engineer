from datetime import date

PACKAGE = "engagement"


def test_charter(cap, cap_data):
    c = cap.parse_notes((cap_data / "discovery_notes.md").read_text(encoding="utf-8"))
    assert c.customer == "Lakeside Community Health"
    assert ("Dr. Amara Okafor", "Chief Medical Officer (exec sponsor)") in c.stakeholders
    m = {x["name"]: x for x in c.metrics}
    assert m["Nurse re-ask time per callback"] == {"name": "Nurse re-ask time per callback", "baseline": 6.0,
                                                   "target": 2.0, "unit": "min"}
    assert len(c.open_questions) == 3 and len(c.constraints) == 3
    assert cap.validate_charter(c) == ["metric 'Patients feel heard' is not measurable"]


def test_assumptions(cap):
    out = cap.assumptions_for(["Who owns the triage red-flag list?", "What is the retention period?",
                               "Do we support Spanish callers?"])
    assert out[0].startswith("Who owns the triage red-flag list? -> Until confirmed, we assume the CMO owns")
    assert "30 days" in out[1]
    assert "most conservative option" in out[2]


def test_engagement_plan(cap):
    plan = cap.engagement_plan(date(2026, 10, 19))            # a Monday
    assert len(plan) == 6 and plan[0][:2] == (1, date(2026, 10, 23))
    assert plan[1][2].startswith("POC demo") and plan[1][1] == date(2026, 10, 30)
    assert plan[-1] == (6, date(2026, 11, 27), "Executive readout and go/no-go")
    assert cap.engagement_plan(date(2026, 10, 23))[0][1] == date(2026, 10, 23)   # starting on a Friday
