import json

import pytest

from fde_kit import FakeLLM

PLAN = [
    {"id": "s3", "worker": "writer", "task": "draft email", "depends_on": ["s1", "s2"], "requires_approval": False},
    {"id": "s1", "worker": "billing", "task": "fetch invoice INV-9", "depends_on": [], "requires_approval": False},
    {"id": "s2", "worker": "logs", "task": "check payment logs", "depends_on": ["s1"], "requires_approval": False},
    {"id": "s4", "worker": "billing", "task": "refund $40", "depends_on": ["s3"], "requires_approval": True},
]


def workers(seen):
    def billing(task, ctx):
        seen.append(("billing", task, dict(ctx)))
        return "invoice total $40, charged twice" if "fetch" in task else "refund R-1 issued"

    def logs(task, ctx):
        seen.append(("logs", task, dict(ctx)))
        return "two captures found"

    def writer(task, ctx):
        seen.append(("writer", task, dict(ctx)))
        return "Dear customer..."

    return {"billing": billing, "logs": logs, "writer": writer}


def test_plan_topological_and_prompt(impl):
    llm = FakeLLM([json.dumps(PLAN)])
    o = impl.Orchestrator(llm, workers([]), approve=lambda s: True)
    steps = o.plan("resolve dispute")
    assert [s.id for s in steps] == ["s1", "s2", "s3", "s4"]
    assert all(w in llm.calls[0]["system"] for w in ("billing", "logs", "writer"))


@pytest.mark.parametrize("bad", [
    [{"id": "a", "worker": "hacker", "task": "x", "depends_on": [], "requires_approval": False}],
    [{"id": "a", "worker": "logs", "task": "x", "depends_on": ["zz"], "requires_approval": False}],
    [{"id": "a", "worker": "logs", "task": "x", "depends_on": ["b"], "requires_approval": False},
     {"id": "b", "worker": "logs", "task": "y", "depends_on": ["a"], "requires_approval": False}],
])
def test_plan_validation(impl, bad):
    with pytest.raises(ValueError):
        impl.Orchestrator(FakeLLM([json.dumps(bad)]), workers([]), approve=lambda s: True).plan("g")


def test_run_approved(impl):
    seen = []
    approvals = []
    o = impl.Orchestrator(FakeLLM([json.dumps(PLAN)]), workers(seen), approve=lambda s: approvals.append(s.id) or True)
    r = o.run("resolve dispute")
    assert r.statuses == {"s1": "done", "s2": "done", "s3": "done", "s4": "done"}
    assert approvals == ["s4"]
    writer_ctx = next(c for w, _, c in seen if w == "writer")
    assert writer_ctx == {"s1": "invoice total $40, charged twice", "s2": "two captures found"}
    assert r.audit[0] == "plan: 4 steps" and "s4: approval requested" in r.audit


def test_run_rejected_and_failure_cascade(impl):
    plan = PLAN + [{"id": "s5", "worker": "writer", "task": "confirm refund", "depends_on": ["s4"], "requires_approval": False}]
    o = impl.Orchestrator(FakeLLM([json.dumps(plan)]), workers([]), approve=lambda s: False)
    r = o.run("g")
    assert r.statuses["s4"] == "rejected" and r.statuses["s5"] == "skipped"
    assert r.audit[-3:] == ["s4: approval requested", "s4: rejected", "s5: skipped"]

    w = workers([])
    w["logs"] = lambda t, c: (_ for _ in ()).throw(TimeoutError("log store slow"))
    r = impl.Orchestrator(FakeLLM([json.dumps(PLAN)]), w, approve=lambda s: True).run("g")
    assert r.statuses == {"s1": "done", "s2": "failed", "s3": "skipped", "s4": "skipped"}
    assert r.outputs["s2"] == "TimeoutError: log store slow"
