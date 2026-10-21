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


def test_boundary_approval_follows_plan_flag(impl):
    """ex46 trusts the planner's requires_approval flag: an unflagged refund runs without approval."""
    plan = [{"id": "s1", "worker": "billing", "task": "refund $40", "depends_on": [], "requires_approval": False}]
    asked = []
    o = impl.Orchestrator(FakeLLM([json.dumps(plan)]), workers([]), approve=lambda s: asked.append(s.id) or False)
    r = o.run("g")
    assert asked == [] and r.statuses == {"s1": "done"}
    assert "s1: approval requested" not in r.audit


def test_policy_approval_overrides_plan_flag(impl):
    """always_approve is policy in code: an unflagged refund still waits for a person, and never runs on a no."""
    plan = [{"id": "s1", "worker": "billing", "task": "refund $40", "depends_on": [], "requires_approval": False}]
    seen = []
    o = impl.Orchestrator(FakeLLM([json.dumps(plan)]), workers(seen), approve=lambda s: False,
                          always_approve={"billing"})
    r = o.run("g")
    assert r.statuses == {"s1": "rejected"} and seen == []
    assert r.audit == ["plan: 1 steps", "s1: approval requested", "s1: rejected"]


@pytest.mark.parametrize("approve", [lambda s: 1 / 0, lambda s: "yes", lambda s: None])
def test_approval_fails_closed(impl, approve):
    seen = []
    r = impl.Orchestrator(FakeLLM([json.dumps(PLAN)]), workers(seen), approve=approve).run("g")
    assert r.statuses["s4"] == "rejected" and ("billing", "refund $40") not in [(w, t) for w, t, _ in seen]


def test_failed_step_has_no_downstream_side_effects(impl):
    seen, asked = [], []
    w = workers(seen)
    w["logs"] = lambda t, c: (_ for _ in ()).throw(ConnectionError("log store down"))
    r = impl.Orchestrator(FakeLLM([json.dumps(PLAN)]), w, approve=lambda s: asked.append(s.id) or True).run("g")
    assert [t for _, t, _ in seen] == ["fetch invoice INV-9"]  # the refund never ran
    assert asked == [] and r.audit[-3:] == ["s2: failed", "s3: skipped", "s4: skipped"]
    assert r.outputs == {"s1": "invoice total $40, charged twice", "s2": "ConnectionError: log store down"}
