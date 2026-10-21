import re

import pytest

PACKAGE = "deliverylead"


@pytest.fixture
def ctx(cap, cap_data):
    eng = cap.load_json(cap_data / "engagement.json")
    reviews = cap.review_all(cap.load_json(cap_data / "partner_deliverables.json"))
    ad = cap.load_json(cap_data / "adoption.json")
    k = ad["kpi"]
    sec = cap.load_json(cap_data / "security.json")
    return dict(eng=eng, reviews=reviews, funnel=cap.funnel(ad["events"]), events=ad["events"],
                impact=cap.diff_in_diff(k["pre_treatment"], k["post_treatment"], k["pre_control"], k["post_control"]),
                security=cap.security_gate(sec["questions"], sec["facts"]), facts=sec["facts"])


def test_partner_reviews(ctx):
    by = {r["id"]: r for r in ctx["reviews"]}
    assert by["D-data-1"]["decision"] == "accept"
    fe = by["D-fe-1"]
    assert fe["decision"] == "reject"
    assert fe["reasons"] == ["blocker findings: 2", "open critical defects: 1", "major findings: 2", "tests 40/46",
                             "eval pass rate 0.88 < 0.9"]
    assert ("blocker", "pii_handling") in fe["findings"] and ("blocker", "rollback") in fe["findings"]


def test_adoption_and_impact(cap, ctx):
    assert ctx["funnel"] == {"invited": 8, "activated": 4, "habitual": 2, "activation_rate": 0.5, "habit_rate": 0.25}
    assert cap.lagging_teams(ctx["events"]) == [("private-banking", 0.25)]
    assert ctx["impact"] == {"treatment_change": -16.75, "control_change": -1.5, "effect": -15.25, "effect_pct": -36.97}


def test_security_gate(cap, ctx):
    s = ctx["security"]
    assert s["status"] == "open" and len(s["answered"]) == 8
    assert [q.split()[2] for q in s["open"]] == ["physical", "model"]
    assert s["answered"]["Is customer data used for model training?"] == "Used for model training: No."
    assert cap.security_gate(["Is data encrypted at rest?"], ctx["facts"])["status"] == "clear"


def test_go_live(cap, ctx):
    fc = cap.forecast(ctx["eng"])
    d = cap.go_live(fc, ctx["reviews"], ctx["security"], ctx["funnel"], ctx["impact"])
    assert d["decision"] == "NO_GO" and len(d["blockers"]) == 2
    assert d["conditions"] == ["activation 50% below 60%"]
    fixed_reviews = [{**r, "decision": "accept", "reasons": []} for r in ctx["reviews"]]
    clear = {**ctx["security"], "status": "clear", "open": []}
    d = cap.go_live(fc, fixed_reviews, clear, ctx["funnel"], ctx["impact"])
    assert d["decision"] == "GO_WITH_CONDITIONS"
    d = cap.go_live(fc, fixed_reviews, clear, {**ctx["funnel"], "activation_rate": 0.75}, ctx["impact"])
    assert d == {"decision": "GO", "blockers": [], "conditions": []}


def test_steering_update(cap, ctx):
    eng = ctx["eng"]
    fc = cap.forecast(eng)
    dec = cap.go_live(fc, ctx["reviews"], ctx["security"], ctx["funnel"], ctx["impact"])
    md = cap.render_steering(eng, cap.workstream_rag(eng), fc, ctx["reviews"], ctx["security"], ctx["funnel"],
                             ctx["impact"], dec)
    assert md.startswith("# Meridian Bank steering update: week 3")
    assert "Status: **RED**" in md and "(+1.5 days)" in md
    assert "| data | Atlas SI | AMBER | -12% |" in md
    assert "| D-fe-1 | Atlas SI | reject |" in md
    assert "-15.25 (-36.97%)" in md and "2 open with the security team" in md
    heads = re.findall(r"^## (.*)$", md, re.M)
    assert heads == ["Decisions needed", "Overall", "Workstreams", "Partner deliverables", "Adoption and impact",
                     "Security"], "lead with the decision, then status, changes, value, risks"
    asks = md.split("## Decisions needed")[1].split("## Overall")[0]
    assert "- activation 50% below 60%" in asks and "D-fe-1" in asks
