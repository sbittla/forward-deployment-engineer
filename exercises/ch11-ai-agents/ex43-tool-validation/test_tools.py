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
