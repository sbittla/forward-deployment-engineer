import json

import pytest

PACKAGE = "opsagent"


@pytest.fixture
def client(cap, cap_data):
    store = cap.OrderStore.from_json(cap_data / "orders.json")
    audit = cap.AuditLog()
    approvals = cap.ApprovalQueue(store, audit)
    registry = cap.build_tools(store, cap.RefundPolicy(), "ana@example.com", approvals, audit)
    c = cap.InProcessClient(cap.MCPServer("orders", registry))
    c.store, c.audit, c.approvals = store, audit, approvals
    return c


def test_handshake_and_listing(client):
    info = client.initialize()
    assert info["capabilities"] == {"tools": {}} and info["serverInfo"]["name"] == "orders"
    tools = {t["name"]: t for t in client.list_tools()}
    assert set(tools) == {"get_order", "list_orders", "issue_refund"}
    assert tools["issue_refund"]["inputSchema"]["required"] == ["order_id", "amount", "reason"]


def test_tools_are_customer_scoped(client):
    text, err = client.call_tool("get_order", {"order_id": "A100"})
    assert not err and json.loads(text)["refunded"] == 0
    text, err = client.call_tool("get_order", {"order_id": "B200"})
    assert err and "not found" in text
    orders = json.loads(client.call_tool("list_orders", {})[0])
    assert {o["order_id"] for o in orders} == {"A100", "A101", "A102", "A103"}


def test_refund_paths(client):
    text, err = client.call_tool("issue_refund", {"order_id": "A100", "amount": 20, "reason": "damaged"})
    assert not err and json.loads(text)["status"] == "refunded"
    text, err = client.call_tool("issue_refund", {"order_id": "A102", "amount": 5, "reason": "x"})
    assert err and "window" in text
    text, err = client.call_tool("issue_refund", {"order_id": "A100", "amount": "lots"})
    assert err and text.startswith("Invalid arguments for issue_refund:") and "reason is required" in text
    assert client.store.refunded_total("A100") == 20


def test_approval_queue(cap, cap_data):
    store = cap.OrderStore.from_json(cap_data / "orders.json")
    audit = cap.AuditLog()
    q = cap.ApprovalQueue(store, audit)
    reg = cap.build_tools(store, cap.RefundPolicy(), "bob@example.com", q, audit)
    text, err = reg.call("issue_refund", {"order_id": "B200", "amount": 120.0, "reason": "defective"})
    assert json.loads(text)["status"] == "pending_approval" and store.refunded_total("B200") == 0
    resolved = q.resolve(q.pending[0]["approval_id"], True, "supervisor:kim")
    assert resolved["approved"] and store.refunded_total("B200") == 120.0
    assert audit.events()[-2:] == ["tool_ok", "approval_resolved"] or "approval_resolved" in audit.events()


def test_protocol_errors(cap, client):
    assert client.server.handle({"jsonrpc": "2.0", "id": 1, "method": "nope"})["error"]["code"] == -32601
    assert client.server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
