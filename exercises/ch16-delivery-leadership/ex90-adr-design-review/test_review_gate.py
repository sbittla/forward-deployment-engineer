import pytest

GOOD = """# ADR-7: Use managed Postgres with pgvector instead of a separate vector database
Status: Accepted

## Context
Security will not approve another datastore; the customer already runs managed Postgres.

## Decision
Store embeddings in Postgres with pgvector and an HNSW index. decided-by: steering committee, 2026-10-12

## Consequences
One fewer system to operate. Trade-off: recall at very large scale is lower than a dedicated engine, and index builds add cost.

## Alternatives considered
- Dedicated vector database (rejected: new vendor review)
- Elasticsearch kNN (rejected: no in-house expertise)
"""


def test_parse(impl):
    adr = impl.parse_adr(GOOD)
    assert adr.number == 7 and adr.status == "accepted" and adr.title.startswith("Use managed Postgres")
    assert set(adr.sections) == {"context", "decision", "consequences", "alternatives considered"}
    with pytest.raises(ValueError):
        impl.parse_adr("# Not an ADR\nStatus: accepted")
    with pytest.raises(ValueError):
        impl.parse_adr("# ADR-1: x\n## Context\nc")


def test_lint(impl):
    assert impl.lint_adr(impl.parse_adr(GOOD)) == []
    bad = (GOOD.replace("decided-by: steering committee, 2026-10-12", "")
              .replace("Trade-off: recall at very large scale is lower than a dedicated engine, and index builds add cost.",
                       "Everything gets better.")
              .replace("- Elasticsearch kNN (rejected: no in-house expertise)\n", ""))
    assert impl.lint_adr(impl.parse_adr(bad)) == ["alternatives:fewer-than-2", "consequences:no-downside",
                                                  "decision:no-owner"]
    proposed = "# ADR-2: Thing\nStatus: proposed\n## Context\nx\n"
    assert impl.lint_adr(impl.parse_adr(proposed)) == ["missing:decision", "missing:consequences",
                                                       "missing:alternatives considered"]


DESIGN = {"auth": "Entra ID OIDC, per-user tokens", "data_flow": "diagram v3", "rollback": "blue/green",
          "pii_handling": "Emails are sent to model for summarisation", "evals": "", "observability": "OTel traces",
          "slo": "99.5%"}


def test_review_design(impl):
    f = impl.review_design(DESIGN)
    assert [(x.severity, x.area) for x in f] == [("blocker", "pii_handling"), ("major", "evals"),
                                                ("major", "threat_model"), ("minor", "cost_estimate")]
    ok = {**DESIGN, "pii_handling": "PII is redacted before being sent to model", "evals": "golden set v2",
          "threat_model": "STRIDE review", "cost_estimate": "$0.01/query"}
    assert impl.review_design(ok) == []


def test_gate(impl):
    F = impl.Finding
    ev = {"tests_passed": 120, "tests_total": 120, "eval_pass_rate": 0.94, "open_criticals": 0}
    assert impl.gate([], ev) == ("accept", [])
    d, reasons = impl.gate([F("major", "evals", "x")], {**ev, "tests_passed": 118, "eval_pass_rate": 0.85})
    assert d == "conditional" and reasons == ["major findings: 1", "tests 118/120", "eval pass rate 0.85 < 0.9"]
    d, reasons = impl.gate([F("blocker", "auth", "x")], {**ev, "open_criticals": 2})
    assert d == "reject" and reasons[:2] == ["blocker findings: 1", "open critical defects: 2"]


RISK = {"risk": "R-12: the red-team covered current policy forms, not endorsements",
        "owner": "Northwind CISO", "owner_org": "Customer",
        "rationale": "Wave 1 is 100 adjusters with read-only answers; endorsements are added in wave 2",
        "compensating_control": "Nightly injection test set, output guardrail, rehearsed kill switch",
        "decided_on": "2026-11-06", "expires": "2026-12-04"}


def test_risk_acceptance(impl):
    assert impl.lint_risk_acceptance(RISK) == []
    assert impl.lint_risk_acceptance({**RISK, "compensating_control": " ", "expires": ""}) == [
        "missing:compensating_control", "missing:expires"]
    # the delivery team or the partner can't accept the customer's risk
    assert impl.lint_risk_acceptance({**RISK, "owner_org": "partner"}) == ["owner:not-customer"]
    # an acceptance with no end, or an end before the decision, isn't a review date
    assert impl.lint_risk_acceptance({**RISK, "expires": "2027-06-30"}) == ["expires:over-90-days"]
    assert impl.lint_risk_acceptance({**RISK, "expires": "2026-11-01"}) == ["expires:not-after-decision"]
    assert impl.lint_risk_acceptance({**RISK, "expires": "next quarter"}) == ["dates:invalid"]
