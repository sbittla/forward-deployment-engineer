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


def mini_server(tools, era="legacy"):
    """A tiny MCP-speaking handler around ToolDefs (stands in for a real server).

    era="legacy": handshake server (2025-06-18, no server/discover).
    era="modern": stateless 2026-07-28 server that requires _meta on every request.
    """
    by_name = {t.name: t for t in tools}
    V = "io.modelcontextprotocol/protocolVersion"

    def handle(msg):
        if "id" not in msg:
            return None
        mid, method, params = msg["id"], msg["method"], msg.get("params", {})
        version = params.get("_meta", {}).get(V)
        if era == "modern":
            if version != "2026-07-28":
                return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32022, "message": "Unsupported protocol version",
                        "data": {"supported": ["2026-07-28"], "requested": version}}}
            wrap = {"resultType": "complete"}
        else:
            wrap = {}
        if method == "server/discover" and era == "modern":
            return {"jsonrpc": "2.0", "id": mid, "result": {**wrap, "supportedVersions": ["2026-07-28"],
                    "capabilities": {"tools": {}},
                    "_meta": {"io.modelcontextprotocol/serverInfo": {"name": "tickets", "version": "2"}}}}
        if method == "initialize" and era == "legacy":
            return {"jsonrpc": "2.0", "id": mid, "result": {"protocolVersion": params["protocolVersion"],
                    "capabilities": {"tools": {}}, "serverInfo": {"name": "tickets", "version": "1"}}}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": mid, "result": {**wrap, "tools": [
                {"name": t.name, "description": t.description, "inputSchema": t.input_schema} for t in tools]}}
        if method == "tools/call":
            t = by_name.get(params["name"])
            if t is None:
                return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": "unknown tool"}}
            try:
                text, err = json.dumps(t.fn(**params["arguments"])), False
            except Exception as e:
                text, err = f"Error: {e}", True
            return {"jsonrpc": "2.0", "id": mid,
                    "result": {**wrap, "content": [{"type": "text", "text": text}], "isError": err}}
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "Method not found"}}
    return handle


def spying(handler, sent):
    def spy(msg):
        sent.append(msg)
        return handler(msg)
    return spy


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


def test_search_wildcards_are_literal(impl, conn):
    conn.execute("INSERT INTO tickets VALUES (4, 'Disk at 95% full', 'open', 'alert')")
    search = {t.name: t for t in impl.make_ticket_tools(conn)}["search_tickets"].fn
    assert [r["id"] for r in search(query="%")] == [4]
    assert [r["id"] for r in search(query="95%")] == [4]
    assert search(query="_") == []


def test_client_modern_server(impl, conn):
    sent = []
    handler = spying(mini_server(impl.make_ticket_tools(conn), "modern"), sent)
    client = impl.MCPClient(impl.InProcessTransport(handler), "smoke-test", "0.1")
    info = client.connect()
    assert info == {"era": "modern", "protocolVersion": "2026-07-28", "serverInfo": {"name": "tickets", "version": "2"},
                    "capabilities": {"tools": {}}}
    assert sent[0]["method"] == "server/discover" and sent[0]["id"] == 1
    meta = sent[0]["params"]["_meta"]
    assert meta["io.modelcontextprotocol/protocolVersion"] == "2026-07-28"
    assert meta["io.modelcontextprotocol/clientInfo"] == {"name": "smoke-test", "version": "0.1"}
    assert {t["name"] for t in client.list_tools()} == {"search_tickets", "get_ticket"}
    assert json.loads(client.call_tool("get_ticket", {"ticket_id": 1}))["title"] == "Login fails with SSO"
    assert all("_meta" in m["params"] for m in sent) and not any(m["method"] == "initialize" for m in sent)
    assert sent[-1]["id"] == 3


def test_client_falls_back_to_legacy(impl, conn):
    sent = []
    handler = spying(mini_server(impl.make_ticket_tools(conn)), sent)
    client = impl.MCPClient(impl.InProcessTransport(handler), "smoke-test", "0.1")
    info = client.connect()
    assert info["era"] == "legacy" and info["protocolVersion"] == "2025-11-25"
    assert info["serverInfo"]["name"] == "tickets"
    assert [m["method"] for m in sent] == ["server/discover", "initialize", "notifications/initialized"]
    assert sent[1]["params"]["clientInfo"] == {"name": "smoke-test", "version": "0.1"}
    assert sent[2] == {"jsonrpc": "2.0", "method": "notifications/initialized"}
    assert {t["name"] for t in client.list_tools()} == {"search_tickets", "get_ticket"}
    assert "_meta" not in sent[-1].get("params", {})
    with pytest.raises(impl.ToolError):
        client.call_tool("get_ticket", {"ticket_id": 42})
    with pytest.raises(impl.RPCError) as e:
        client.call_tool("nope", {})
    assert e.value.code == -32602


def test_unsupported_version_picks_from_server_list(impl):
    """A server that rejects 2026-07-28 with -32022 lists what it supports; the client picks a shared version."""
    calls = []

    def handler(msg):
        calls.append(msg)
        if "id" not in msg:
            return None
        if msg["method"] == "initialize":
            return {"jsonrpc": "2.0", "id": msg["id"], "result": {"protocolVersion": msg["params"]["protocolVersion"],
                    "capabilities": {}, "serverInfo": {"name": "old", "version": "1"}}}
        v = msg.get("params", {}).get("_meta", {}).get("io.modelcontextprotocol/protocolVersion")
        return {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32022, "message": "Unsupported protocol version",
                "data": {"supported": ["2025-06-18", "2025-03-26"], "requested": v}}}

    info = impl.MCPClient(impl.InProcessTransport(handler)).connect()
    assert info["era"] == "legacy" and info["protocolVersion"] == "2025-06-18"
    assert calls[1]["params"]["protocolVersion"] == "2025-06-18"


def test_rpc_error_keeps_data(impl):
    err = impl.RPCError(-32022, "Unsupported protocol version", {"supported": ["x"]})
    assert err.code == -32022 and err.data == {"supported": ["x"]}


SERVER_SCRIPT = textwrap.dedent('''
    import json, sys
    for line in sys.stdin:
        msg = json.loads(line)
        if "id" not in msg:
            continue
        # emit an unrelated notification first to make sure the client skips it
        print(json.dumps({"jsonrpc": "2.0", "method": "notifications/message", "params": {"level": "info"}}), flush=True)
        if msg["method"] == "server/discover":
            print(json.dumps({"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32601, "message": "Method not found"}}), flush=True)
            continue
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
        assert c.connect()["serverInfo"]["name"] == "echo" and c.era == "legacy"
        assert c.list_tools()[0]["name"] == "echo"
        assert c.call_tool("echo", {"who": "world"}) == "hello world"
    finally:
        t.close()
