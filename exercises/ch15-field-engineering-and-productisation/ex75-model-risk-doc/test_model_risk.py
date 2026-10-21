import copy

META = {
    "name": "Claims Copilot", "version": "1.2", "owner": "Claims Platform", "purpose": "Draft answers for adjusters",
    "users": "Internal claims adjusters", "out_of_scope": ["Claim approval decisions", "Direct customer chat"],
    "customer_facing": False, "automated_decision": False, "regulated_domain": True,
    "data_sources": ["Policy documents", "Resolved tickets (redacted)"], "model_provider": "Anthropic Claude via API",
    "evals": [{"name": "groundedness", "metric": "pass rate", "value": 0.96, "threshold": 0.95},
              {"name": "safety", "metric": "violations per 1k", "value": 0.0, "threshold": 0.0}],
    "limitations": ["English only"], "monitoring": ["Weekly eval re-run", "SLO dashboard"],
    "human_oversight": "Adjusters review every draft before sending",
}


def test_tiers(impl):
    assert impl.risk_tier(META) == 2
    assert impl.risk_tier({**META, "automated_decision": True}) == 1
    assert impl.risk_tier({**META, "regulated_domain": False}) == 3
    assert impl.risk_tier({**META, "regulated_domain": False, "automated_decision": True}) == 2


def test_controls(impl):
    assert impl.required_controls(3) == ["eval suite", "owner sign-off"]
    assert impl.required_controls(1) == ["eval suite", "owner sign-off", "monitoring dashboard",
                                         "human review of samples", "independent validation", "MRM approval",
                                         "kill switch"]


def test_validate(impl):
    assert impl.validate(META) == []
    bad = copy.deepcopy(META)
    del bad["owner"]
    bad["limitations"] = []
    del bad["customer_facing"]
    bad["evals"][0]["value"] = 0.90
    bad["automated_decision"] = True
    bad["human_oversight"] = "Logs are kept"
    issues = impl.validate(bad)
    assert set(issues) == {"missing:owner", "missing:limitations", "missing:customer_facing",
                           "eval_below_threshold:groundedness", "tier1_requires_human_oversight"}


def test_render(impl):
    md = impl.render(META)
    heads = [l for l in md.splitlines() if l.startswith("#")]
    assert heads == ["# Model risk document: Claims Copilot v1.2", "## Summary", "## Intended use", "## Out of scope",
                     "## Data", "## Evaluation", "## Limitations", "## Monitoring", "## Human oversight",
                     "## Required controls", "## Approval"]
    assert "| groundedness | pass rate | 0.96 | 0.95 | PASS |" in md
    assert "Risk tier: 2" in md and "- human review of samples" in md
    assert "Status: READY FOR REVIEW" in md
    bad = {**META, "evals": [{"name": "groundedness", "metric": "pass rate", "value": 0.5, "threshold": 0.95}]}
    out = impl.render(bad)
    assert "| groundedness | pass rate | 0.5 | 0.95 | FAIL |" in out and "Status: BLOCKED (1 issues)" in out
