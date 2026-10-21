import json

import pytest

REFUND_SCHEMA = {
    "type": "object",
    "required": ["order_id", "amount"],
    "additionalProperties": False,
    "properties": {
        "order_id": {"type": "string"},
        "amount": {"type": "number", "minimum": 0.01, "maximum": 500},
        "reason": {"enum": ["damaged", "late", "other"]},
    },
}


@pytest.fixture
def reg(impl):
    r = impl.ToolRegistry(max_result_chars=50)
    r.calls = []

    def refund(order_id, amount, reason="other"):
        r.calls.append((order_id, amount))
        return {"refund_id": f"R-{len(r.calls)}", "amount": amount}

    def lookup(q):
        if q == "boom":
            raise RuntimeError("password=hunter2 at db.internal:5432")
        return "x" * 120

    r.register("issue_refund", "Refund an order", REFUND_SCHEMA, refund, side_effect=True)
    r.register("search_kb", "Search", {"type": "object", "required": ["q"], "properties": {"q": {"type": "string"}}}, lookup)
    return r


def test_specs(reg):
    assert [s["name"] for s in reg.specs()] == ["issue_refund", "search_kb"]
    assert reg.specs()[0]["input_schema"] == REFUND_SCHEMA


def test_ok(reg):
    res = reg.dispatch("c1", "issue_refund", {"order_id": "A1", "amount": 20})
    assert not res.is_error and json.loads(res.content)["refund_id"] == "R-1"


def test_invalid_lists_all_problems(reg):
    res = reg.dispatch("c2", "issue_refund", {"amount": "50 dollars", "reason": "bored", "note": "x"})
    assert res.is_error and res.content.startswith("Invalid arguments for issue_refund:")
    lines = [l for l in res.content.splitlines() if l.startswith("- ")]
    text = res.content
    assert len(lines) == 4 and "order_id" in text and "amount" in text and "reason" in text and "note" in text
    assert reg.calls == []


def test_range(reg):
    assert reg.dispatch("c3", "issue_refund", {"order_id": "A", "amount": 900}).is_error


def test_unknown(reg):
    res = reg.dispatch("c4", "delete_db", {})
    assert res.is_error and res.content == "Unknown tool 'delete_db'. Available: issue_refund, search_kb"


def test_exception_sanitised(reg):
    res = reg.dispatch("c5", "search_kb", {"q": "boom"})
    assert res.is_error and res.content == "Tool search_kb failed: RuntimeError" and "hunter2" not in res.content


def test_truncation(reg):
    res = reg.dispatch("c6", "search_kb", {"q": "ok"})
    assert res.content == "x" * 50 + "... [truncated 70 chars]"


def test_side_effect_once_per_call_id(reg):
    a = reg.dispatch("same", "issue_refund", {"order_id": "A1", "amount": 20})
    b = reg.dispatch("same", "issue_refund", {"order_id": "A1", "amount": 20})
    assert a.content == b.content and len(reg.calls) == 1
    reg.dispatch("other", "issue_refund", {"order_id": "A1", "amount": 20})
    assert len(reg.calls) == 2


def test_malformed_arguments_rejected(reg):
    # A model can emit truncated JSON or no arguments object at all; neither reaches the tool.
    for bad in ('{"order_id": "A1", "amount": 2', None, ["A1", 20]):
        res = reg.dispatch("m1", "issue_refund", bad)
        assert res.is_error and res.content.startswith("Invalid arguments for issue_refund:\n- arguments must be a object")
    assert reg.calls == []


@pytest.fixture
def secure(impl):
    r = impl.ToolRegistry()
    r.calls = []

    def refund(order_id, amount, reason="other"):
        r.calls.append((order_id, amount))
        return {"refund_id": f"R-{len(r.calls)}"}

    def lookup(q):
        if q == "boom":
            raise RuntimeError("db down")
        return "ok"

    r.register("issue_refund", "Refund an order", REFUND_SCHEMA, refund, side_effect=True, roles={"supervisor"},
               idempotency_key=lambda a: f"{a['order_id']}:{a['amount']}")
    r.register("search_kb", "Search", {"type": "object", "required": ["q"], "properties": {"q": {"type": "string"}}},
               lookup, roles={"agent", "supervisor"})
    r.register("drop_index", "Admin only, no roles granted", {"type": "object"}, lambda: "dropped")
    return r


def test_least_privilege_dispatch_as(secure):
    assert [s["name"] for s in secure.specs_for("agent")] == ["search_kb"]
    assert [s["name"] for s in secure.specs_for("supervisor")] == ["issue_refund", "search_kb"]
    res = secure.dispatch_as("agent", "c1", "issue_refund", {"order_id": "A1", "amount": 20})
    assert res.is_error and res.content == "Not permitted: issue_refund for role agent" and secure.calls == []
    assert secure.dispatch_as("supervisor", "c2", "drop_index", {}).content == "Not permitted: drop_index for role supervisor"
    assert secure.dispatch_as("supervisor", "c3", "delete_db", {}).content == "Not permitted: delete_db for role supervisor"
    assert not secure.dispatch_as("supervisor", "c4", "issue_refund", {"order_id": "A1", "amount": 20}).is_error
    assert secure.calls == [("A1", 20)]


def test_idempotency_key_runs_once_across_call_ids(secure):
    first = secure.dispatch_as("supervisor", "c1", "issue_refund", {"order_id": "A1", "amount": 20})
    retry = secure.dispatch_as("supervisor", "c2", "issue_refund", {"order_id": "A1", "amount": 20, "reason": "late"})
    assert retry.call_id == "c2" and retry.content == first.content and not retry.is_error
    assert secure.calls == [("A1", 20)]
    secure.dispatch_as("supervisor", "c3", "issue_refund", {"order_id": "A1", "amount": 25})
    assert secure.calls == [("A1", 20), ("A1", 25)]


def test_audit_entry_per_call_including_denied(secure):
    secure.dispatch_as("agent", "c1", "issue_refund", {"order_id": "A1", "amount": 20})
    secure.dispatch_as("supervisor", "c2", "issue_refund", {"order_id": "A1"})
    secure.dispatch_as("supervisor", "c3", "issue_refund", {"order_id": "A1", "amount": 20})
    secure.dispatch_as("supervisor", "c3", "issue_refund", {"order_id": "A1", "amount": 20})
    secure.dispatch_as("agent", "c4", "search_kb", {"q": "boom"})
    secure.dispatch("c5", "teleport", {})
    log = secure.audit_log()
    assert log == (("c1", "issue_refund", "agent", "denied"), ("c2", "issue_refund", "supervisor", "invalid"),
                   ("c3", "issue_refund", "supervisor", "ok"), ("c3", "issue_refund", "supervisor", "replayed"),
                   ("c4", "search_kb", "agent", "failed"), ("c5", "teleport", None, "unknown"))
    assert isinstance(log, tuple)  # a copy: callers can't edit or drop entries
    secure.dispatch_as("agent", "c6", "search_kb", {"q": "x"})
    assert secure.audit_log()[:6] == log and secure.audit_log()[6] == ("c6", "search_kb", "agent", "ok")
