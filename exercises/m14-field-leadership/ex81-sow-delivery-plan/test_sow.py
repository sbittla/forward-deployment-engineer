import math
import re
from datetime import date

import pytest


@pytest.fixture
def tasks(impl):
    T = impl.Task
    return [
        T("disc", "Discovery", 2, 3, 4, milestone="Charter signed"),
        T("data", "Data access & ingest", 3, 5, 13, ("disc",)),
        T("ui", "Agent desktop widget", 2, 4, 6, ("disc",)),
        T("rag", "RAG + evals", 4, 6, 8, ("data",), milestone="POC demo"),
        T("sec", "Security review", 2, 3, 10, ("disc",)),
        T("prod", "Production rollout", 2, 3, 4, ("rag", "ui", "sec"), milestone="Go-live"),
    ]


def test_pert(impl, tasks):
    assert impl.pert(tasks[1]) == (6.0, 1.67)


def test_schedule_and_critical_path(impl, tasks):
    s = impl.schedule(tasks)
    assert (s["disc"].start, s["disc"].finish) == (0, 3.0)
    assert s["data"].finish == 9.0 and s["rag"].finish == 15.0 and s["prod"].start == 15.0
    assert s["ui"].slack == 8.0 and not s["ui"].critical
    assert s["sec"].slack == 8.0          # expected (2 + 4*3 + 10) / 6 = 4.0; finishes day 7, prod starts day 15
    assert impl.critical_path(tasks) == ["disc", "data", "rag", "prod"]


def test_estimate(impl, tasks):
    p50, p90 = impl.project_estimate(tasks)
    var = sum(((p - o) / 6) ** 2 for o, p in [(2, 4), (3, 13), (4, 8), (2, 4)])
    assert p50 == 18.0 and p90 == round(18 + 1.2816 * math.sqrt(var), 1)


def test_cycles_and_unknown(impl):
    T = impl.Task
    with pytest.raises(ValueError):
        impl.schedule([T("a", "A", 1, 1, 1, ("b",)), T("b", "B", 1, 1, 1, ("a",))])
    with pytest.raises(ValueError):
        impl.schedule([T("a", "A", 1, 1, 1, ("zzz",))])


def test_working_days(impl):
    assert impl.to_dates(0, date(2026, 10, 19)) == date(2026, 10, 19)        # Monday
    assert impl.to_dates(5, date(2026, 10, 19)) == date(2026, 10, 26)
    assert impl.to_dates(0, date(2026, 10, 24)) == date(2026, 10, 26)        # Saturday -> Monday
    assert impl.to_dates(4, date(2026, 10, 22)) == date(2026, 10, 28)


ENG = {
    "objectives": ["Cut coverage-question handle time from 11 to 8 minutes"],
    "in_scope": ["Policy Q&A copilot for claims adjusters"], "out_of_scope": ["Claim approvals"],
    "assumptions": ["Policy PDFs are text-extractable"], "customer_responsibilities": ["Provide SSO metadata by week 2"],
    "acceptance": {"Charter signed": "Sponsor signs charter", "POC demo": "Golden-set pass rate >= 85%",
                   "Go-live": "Launch bar met; runbook accepted by Claims Platform"},
}


def test_render_sow(impl, tasks):
    md = impl.render_sow(ENG, tasks, date(2026, 10, 19), rate_per_day=2000)
    heads = re.findall(r"^## (.*)$", md, re.M)
    assert heads == ["Objectives", "In scope", "Out of scope", "Deliverables and acceptance criteria", "Timeline",
                     "Assumptions", "Customer responsibilities", "Change control", "Estimate"]
    assert "| Charter signed | 2026-10-21 | Sponsor signs charter |" in md
    assert "| Go-live | 2026-11-11 | Launch bar met; runbook accepted by Claims Platform |" in md
    assert "disc -> data -> rag -> prod" in md
    assert "P50: 18.0 days ($36,000)" in md and "P90:" in md


def test_missing_acceptance(impl, tasks):
    eng = {**ENG, "acceptance": {"POC demo": "x"}}
    with pytest.raises(ValueError):
        impl.render_sow(eng, tasks, date(2026, 10, 19), 2000)
