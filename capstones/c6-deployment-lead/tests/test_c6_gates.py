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
    assert heads == ["Decisions needed", "Overall", "Changed since last week", "Adoption and impact", "Risks and asks",
                     "Next milestone"], "Section 16.3's order: decision, status, changes, value, risks and asks, next"
    assert re.findall(r"^### (.*)$", md, re.M) == ["Workstreams", "Partner deliverables"]
    asks = md.split("## Decisions needed")[1].split("## Overall")[0]
    assert "- activation 50% below 60%" in asks and "D-fe-1" in asks


def _steering(cap, ctx, eng):
    fc = cap.forecast(eng)
    dec = cap.go_live(fc, ctx["reviews"], ctx["security"], ctx["funnel"], ctx["impact"])
    return cap.render_steering(eng, cap.workstream_rag(eng), fc, ctx["reviews"], ctx["security"], ctx["funnel"],
                               ctx["impact"], dec)


def _section(md, name):
    return md.split(f"## {name}\n")[1].split("\n## ")[0]


def test_steering_changes_risks_and_next_milestone(cap, ctx):
    md = _steering(cap, ctx, ctx["eng"])
    changed = _section(md, "Changed since last week")
    assert "- Delivered: landing-zone." in changed
    assert "- Slipped or newly at risk: data GREEN -> AMBER; agent GREEN -> AMBER." in changed
    assert "- Forecast finish: day 24.8, was day 24.1 last week (+0.7 days)." in changed
    risks = _section(md, "Risks and asks").strip().splitlines()
    assert [r.split()[1] for r in risks[:3]] == ["A-1", "R-3", "R-4"], "open items only, by due date"
    assert risks[0].endswith("(owner: Meridian CISO office, due 2026-11-25)")
    assert risks[3] == "- Security: 8 questions auto-answered from system facts; 2 open with the security team."
    assert _section(md, "Next milestone").strip() == (
        "- Eval bar met (agent-evals): forecast day 22.4 vs baseline 21.3. Acceptance: held-out pass rate of at least "
        "0.9 on the bank's golden set, no critical-slice regressions.")
    # a risk without an owner or date is shown as a gap, not hidden; no snapshot means no invented changes
    eng = {k: v for k, v in ctx["eng"].items() if k != "last_week"}
    eng["raid"] = [{"id": "R-9", "type": "risk", "text": "Vendor outage", "status": "open"}]
    md = _steering(cap, ctx, eng)
    assert "- R-9 risk: Vendor outage (owner: UNASSIGNED, due NO DATE)" in md
    assert _section(md, "Changed since last week").startswith("- No previous snapshot to compare with.")
