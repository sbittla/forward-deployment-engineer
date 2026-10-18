import json
import sqlite3
import sys
import textwrap

import pytest


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE tickets(id INTEGER PRIMARY KEY, title TEXT, status TEXT, body TEXT)")
    c.executemany("INSERT INTO tickets VALUES (?,?,?,?)", [
        (1, "Login fails with SSO", "open", "user cannot sign in"),
        (2, "Invoice duplicated", "closed", "charged twice"),
        (3, "SSO certificate expired", "closed", "rotate cert"),
    ])
    return c


def mini_server(tools):
    """A tiny MCP-speaking handler around ToolDefs (stands in for a real server)."""
    by_name = {t.name: t for t in tools}

    def handle(msg):
        if "id" not in msg:
            return None
        mid, method, params = msg["id"], msg["method"], msg.get("params", {})
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": mid, "result": {"protocolVersion": params["protocolVersion"],
                    "capabilities": {"tools": {}}, "serverInfo": {"name": "tickets", "version": "1"}}}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": mid, "result": {"tools": [
                {"name": t.name, "description": t.description, "inputSchema": t.input_schema} for t in tools]}}
        if method == "tools/call":
            t = by_name.get(params["name"])
            if t is None:
                return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": "unknown tool"}}
            try:
                text, err = json.dumps(t.fn(**params["arguments"])), False
            except Exception as e:
                text, err = f"Error: {e}", True
            return {"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": text}], "isError": err}}
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "nope"}}
    return handle


def test_connector_tools(impl, conn):
    tools = {t.name: t for t in impl.make_ticket_tools(conn)}
    assert set(tools) == {"search_tickets", "get_ticket"}
    assert [r["id"] for r in tools["search_tickets"].fn(query="sso")] == [1, 3]
    assert tools["search_tickets"].fn(query="sso", status="closed") == [{"id": 3, "title": "SSO certificate expired", "status": "closed"}]
    assert tools["get_ticket"].fn(ticket_id=2)["body"] == "charged twice"
    with pytest.raises(KeyError):
        tools["get_ticket"].fn(ticket_id=99)
    with pytest.raises(ValueError):
        tools["search_tickets"].fn(query="x", limit=500)
    assert tools["search_tickets"].fn(query="'; DROP TABLE tickets; --") == []
    assert conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] == 3


def test_client_in_process(impl, conn):
    sent = []
    handler = mini_server(impl.make_ticket_tools(conn))

    def spy(msg):
        sent.append(msg)
        return handler(msg)

    client = impl.MCPClient(impl.InProcessTransport(spy))
    info = client.initialize("smoke-test", "0.1")
    assert info["serverInfo"]["name"] == "tickets"
    assert sent[0]["id"] == 1 and sent[0]["params"]["clientInfo"] == {"name": "smoke-test", "version": "0.1"}
    assert sent[1] == {"jsonrpc": "2.0", "method": "notifications/initialized"}
    assert {t["name"] for t in client.list_tools()} == {"search_tickets", "get_ticket"}
    assert json.loads(client.call_tool("get_ticket", {"ticket_id": 1}))["title"] == "Login fails with SSO"
    assert sent[-1]["id"] == 3
    with pytest.raises(impl.ToolError):
        client.call_tool("get_ticket", {"ticket_id": 42})
    with pytest.raises(impl.RPCError) as e:
        client.call_tool("nope", {})
    assert e.value.code == -32602


SERVER_SCRIPT = textwrap.dedent('''
    import json, sys
    for line in sys.stdin:
        msg = json.loads(line)
        if "id" not in msg:
            continue
        # emit an unrelated notification first to make sure the client skips it
        print(json.dumps({"jsonrpc": "2.0", "method": "notifications/message", "params": {"level": "info"}}), flush=True)
        if msg["method"] == "initialize":
            res = {"protocolVersion": msg["params"]["protocolVersion"], "capabilities": {}, "serverInfo": {"name": "echo", "version": "1"}}
        elif msg["method"] == "tools/list":
            res = {"tools": [{"name": "echo", "description": "", "inputSchema": {"type": "object"}}]}
        else:
            res = {"content": [{"type": "text", "text": "hello "}, {"type": "text", "text": msg["params"]["arguments"]["who"]}], "isError": False}
        print(json.dumps({"jsonrpc": "2.0", "id": msg["id"], "result": res}), flush=True)
''')


def test_client_stdio(impl, tmp_path):
    script = tmp_path / "echo_server.py"
    script.write_text(SERVER_SCRIPT)
    t = impl.StdioTransport([sys.executable, str(script)])
    try:
        c = impl.MCPClient(t)
        assert c.initialize("x", "1")["serverInfo"]["name"] == "echo"
        assert c.list_tools()[0]["name"] == "echo"
        assert c.call_tool("echo", {"who": "world"}) == "hello world"
    finally:
        t.close()
