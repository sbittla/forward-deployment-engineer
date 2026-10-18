import io
import json
import subprocess
import sys

import pytest


@pytest.fixture
def server(impl):
    s = impl.MCPServer("policy-db", "0.1.0")

    @s.tool("add", "Add two numbers", {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}})
    def add(a, b):
        return a + b

    @s.tool("fail", "Always fails", {"type": "object"})
    def fail():
        raise ValueError("database offline")

    return s


def rpc(method, params=None, id=1):
    m = {"jsonrpc": "2.0", "id": id, "method": method}
    if params is not None:
        m["params"] = params
    return m


def test_initialize(server, impl):
    r = server.handle(rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                         "clientInfo": {"name": "t", "version": "1"}}))
    assert r["jsonrpc"] == "2.0" and r["id"] == 1
    assert r["result"]["protocolVersion"] == "2025-03-26"
    assert r["result"]["capabilities"] == {"tools": {}}
    assert r["result"]["serverInfo"] == {"name": "policy-db", "version": "0.1.0"}
    r = server.handle(rpc("initialize", {"protocolVersion": "1999-01-01"}))
    assert r["result"]["protocolVersion"] == impl.LATEST


def test_notifications_get_no_response(server):
    assert server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    assert server.handle({"jsonrpc": "2.0", "method": "tools/list"}) is None


def test_list_and_call(server):
    tools = server.handle(rpc("tools/list"))["result"]["tools"]
    assert [t["name"] for t in tools] == ["add", "fail"]
    assert tools[0]["inputSchema"]["properties"]["a"]["type"] == "number"
    r = server.handle(rpc("tools/call", {"name": "add", "arguments": {"a": 2, "b": 3}}, id=7))
    assert r["id"] == 7 and r["result"] == {"content": [{"type": "text", "text": "5"}], "isError": False}


def test_tool_error_is_result_not_protocol_error(server):
    r = server.handle(rpc("tools/call", {"name": "fail", "arguments": {}}))
    assert "error" not in r and r["result"]["isError"] is True
    assert r["result"]["content"][0]["text"] == "Error: database offline"


@pytest.mark.parametrize("msg,code", [
    ({"jsonrpc": "2.0", "id": 1, "method": "nope"}, -32601),
    ({"jsonrpc": "1.0", "id": 1, "method": "ping"}, -32600),
    ({"jsonrpc": "2.0", "id": 1}, -32600),
    ({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "zzz", "arguments": {}}}, -32602),
    ({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "add", "arguments": "x"}}, -32602),
])
def test_errors(server, msg, code):
    r = server.handle(msg)
    assert r["error"]["code"] == code and r["id"] == 1 and "result" not in r


def test_ping(server):
    assert server.handle(rpc("ping"))["result"] == {}


def test_serve_stdio(server):
    lines = [json.dumps(rpc("ping", id=1)), "{not json",
             json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
             json.dumps(rpc("tools/call", {"name": "add", "arguments": {"a": 1, "b": 1}}, id=2))]
    out = io.StringIO()
    server.serve(io.StringIO("\n".join(lines) + "\n"), out)
    replies = [json.loads(l) for l in out.getvalue().splitlines()]
    assert [r.get("id") for r in replies] == [1, None, 2]
    assert replies[1]["error"]["code"] == -32700


def test_demo_server_subprocess(exercise_dir):
    script = next(p for p in exercise_dir.glob("s*.py"))
    msgs = [rpc("initialize", {"protocolVersion": "2025-06-18"}, id=1),
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            rpc("tools/list", id=2),
            rpc("tools/call", {"name": "lookup_policy", "arguments": {"policy_id": "P-100"}}, id=3),
            rpc("tools/call", {"name": "lookup_policy", "arguments": {"policy_id": "X"}}, id=4)]
    proc = subprocess.run([sys.executable, str(script)], input="\n".join(json.dumps(m) for m in msgs) + "\n",
                          capture_output=True, text=True, timeout=20)
    replies = {r["id"]: r for r in (json.loads(l) for l in proc.stdout.splitlines() if l.strip())}
    assert set(replies) == {1, 2, 3, 4}
    assert [t["name"] for t in replies[2]["result"]["tools"]] == ["lookup_policy"]
    assert json.loads(replies[3]["result"]["content"][0]["text"]) == {"policy_id": "P-100", "status": "active"}
    assert replies[4]["result"]["isError"] is True
