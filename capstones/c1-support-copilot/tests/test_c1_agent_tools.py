"""Extend stage: a constrained, consequential tool with authorization, approval, idempotency and a budget."""
import importlib

import pytest

from fde_kit import ToolCall

PACKAGE = "copilot"


@pytest.fixture
def env(cap, cap_data):
    tools = importlib.import_module("copilot.tools")
    tenancy = importlib.import_module("copilot.tenancy")
    who = tenancy.load_principals(cap_data / "principals.json")
    return tools, tools.ClaimReviewTool(tools.load_claims(cap_data / "claims.json")), who


def _code(fn):
    with pytest.raises(Exception) as e:
        fn()
    return getattr(e.value, "code", repr(e.value))


def test_tool_requires_authorization(env):
    tools, tool, who = env
    approval = tools.Approval(who["supervisor"], "HM-55210")

    def call(principal, claim, key):
        return lambda: tool.open_claim_review(principal, claim, "water damage", idempotency_key=key,
                                              budget=tools.ExecutionBudget(), approval=approval)

    assert _code(call(who["adjuster"], "HM-55210", "k1")) == "forbidden"     # another tenant's claim
    assert _code(call(who["adjuster"], "CL-30112", "k2")) == "forbidden"     # same tenant, not assigned
    assert _code(call(who["adjuster"], "CL-99999", "k3")) == "forbidden"     # unknown claim: same answer
    assert _code(call(who["harbor_supervisor"], "CL-20931", "k4")) == "forbidden"
    assert tool.reviews == {} and [a["outcome"] for a in tool.audit] == ["forbidden"] * 4


def test_tool_requires_valid_approval(env):
    tools, tool, who = env
    b = tools.ExecutionBudget(max_calls=10)
    r = tool.open_claim_review(who["adjuster"], "CL-20931", "late notice", idempotency_key="k1", budget=b)
    assert r["status"] == "pending_approval" and tool.reviews == {}
    bad = [tools.Approval(who["adjuster_2"], "CL-20931"),          # not a supervisor
           tools.Approval(who["harbor_supervisor"], "CL-20931"),   # another tenant
           tools.Approval(who["supervisor"], "CL-30112")]          # approval for a different claim
    for a in bad:
        attempt = lambda: tool.open_claim_review(who["adjuster"], "CL-20931", "late notice",  # noqa: E731
                                                 idempotency_key="k1", budget=b, approval=a)
        assert _code(attempt) == "approval_invalid"
    self_approval = tools.Approval(who["supervisor"], "CL-20931")  # a supervisor can't approve their own request
    assert _code(lambda: tool.open_claim_review(who["supervisor"], "CL-20931", "x", idempotency_key="k2", budget=b,
                                                approval=self_approval)) == "approval_invalid"
    ok = tool.open_claim_review(who["adjuster"], "CL-20931", "late notice", idempotency_key="k1", budget=b,
                                approval=tools.Approval(who["supervisor"], "CL-20931"))
    assert ok["status"] == "opened" and tool.reviews[ok["review_id"]]["approved_by"] == "u-dana"
    assert tool.audit[-1]["outcome"] == "opened"


def test_tool_is_idempotent(env):
    tools, tool, who = env
    a = tools.Approval(who["supervisor"], "CL-20931")
    b = tools.ExecutionBudget(max_calls=10)
    key = "req-7:CL-20931"
    first = tool.open_claim_review(who["adjuster"], "CL-20931", "late notice", idempotency_key=key, budget=b,
                                   approval=a)
    again = tool.open_claim_review(who["adjuster"], "CL-20931", "late notice", idempotency_key=key, budget=b,
                                   approval=a)
    assert again["replayed"] and again["review_id"] == first["review_id"] and len(tool.reviews) == 1
    assert _code(lambda: tool.open_claim_review(who["adjuster"], "CL-20931", "other reason", idempotency_key=key,
                                                budget=b, approval=a)) == "idempotency_conflict"


def test_execution_budget_stops_runaway_tool_calls(env):
    tools, tool, who = env
    calls = [ToolCall(f"t{i}", "open_claim_review", {"claim_id": "CL-20931", "reason": f"r{i}"}) for i in range(4)]
    calls.insert(1, ToolCall("tx", "delete_claim", {"claim_id": "CL-20931"}))
    out = tools.execute_tool_calls(calls, tool, who["adjuster"], "req-9", tools.ExecutionBudget(max_calls=2),
                                   approvals={"CL-20931": tools.Approval(who["supervisor"], "CL-20931")})
    assert [o.get("error") or o["status"] for o in out] == [
        "opened", "unknown_tool", "idempotency_conflict", "budget_exceeded", "budget_exceeded"]
    assert len(tool.reviews) == 1
    # an injected call for another tenant's claim is refused, whatever the model was told
    out = tools.execute_tool_calls([ToolCall("t9", "open_claim_review", {"claim_id": "HM-55210", "reason": "x"})],
                                   tool, who["adjuster"], "req-10", tools.ExecutionBudget())
    assert out == [{"status": "error", "error": "forbidden", "claim_id": "HM-55210"}]
