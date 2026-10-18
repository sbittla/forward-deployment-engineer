import io
import json
import subprocess
import sys

import pytest

V = "2026-07-28"
META = {"io.modelcontextprotocol/protocolVersion": V, "io.modelcontextprotocol/clientInfo": {"name": "t", "version": "1"},
        "io.modelcontextprotocol/clientCapabilities": {}}


@pytest.fixture
def server(impl):
    s = impl.MCPServer("policy-db", "0.2.0", instructions="Look up insurance policies.")

    @s.tool("add", "Add two numbers", {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}})
    def add(a, b):
        return a + b

    @s.tool("get_policy", "Policy as structured data", {"type": "object", "properties": {"id": {"type": "string"}}})
    def get_policy(id):
        return {"id": id, "status": "active"}

    @s.tool("fail", "Always fails", {"type": "object", "additionalProperties": False})
    def fail():
        raise ValueError("database offline")

    return s


def modern(method, params=None, id=1, version=V):
    p = dict(params or {})
    p["_meta"] = {**META, "io.modelcontextprotocol/protocolVersion": version}
    return {"jsonrpc": "2.0", "id": id, "method": method, "params": p}


def legacy(method, params=None, id=1):
    m = {"jsonrpc": "2.0", "id": id, "method": method}
    if params is not None:
        m["params"] = params
    return m


def test_discover(server):
    r = server.handle(modern("server/discover"))["result"]
    assert r["resultType"] == "complete" and r["supportedVersions"] == ["2026-07-28"]
    assert r["capabilities"] == {"tools": {}} and r["instructions"] == "Look up insurance policies."
    assert r["_meta"]["io.modelcontextprotocol/serverInfo"] == {"name": "policy-db", "version": "0.2.0"}
    assert r["ttlMs"] == 3600000


def test_modern_list_and_call(server):
    r = server.handle(modern("tools/list"))["result"]
    assert [t["name"] for t in r["tools"]] == ["add", "get_policy", "fail"] and r["ttlMs"] == 300000
    assert r["tools"][0]["inputSchema"]["properties"]["a"]["type"] == "number"
    c = server.handle(modern("tools/call", {"name": "add", "arguments": {"a": 2, "b": 3}}, id=7))
    assert c["id"] == 7 and c["result"] == {"resultType": "complete", "content": [{"type": "text", "text": "5"}],
                                             "isError": False}
    s = server.handle(modern("tools/call", {"name": "get_policy", "arguments": {"id": "P-1"}}))["result"]
    assert s["structuredContent"] == {"id": "P-1", "status": "active"}
    assert json.loads(s["content"][0]["text"]) == {"id": "P-1", "status": "active"}


def test_tool_error_is_result(server):
    r = server.handle(modern("tools/call", {"name": "fail", "arguments": {}}))
    assert "error" not in r and r["result"]["isError"] is True
    assert r["result"]["content"][0]["text"] == "Error: database offline"


def test_unsupported_version(server, impl):
    r = server.handle(modern("tools/list", version="1900-01-01"))
    assert r["error"]["code"] == -32022 and r["error"]["message"] == "Unsupported protocol version"
    assert r["error"]["data"] == {"supported": list(impl.MODERN_VERSIONS + impl.LEGACY_VERSIONS), "requested": "1900-01-01"}


def test_missing_meta_without_handshake(server):
    r = server.handle(legacy("tools/list"))
    assert r["error"]["code"] == -32602 and "io.modelcontextprotocol/protocolVersion" in r["error"]["message"]


def test_legacy_client_still_works(server, impl):
    r = server.handle(legacy("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                            "clientInfo": {"name": "old", "version": "1"}}))["result"]
    assert r["protocolVersion"] == "2025-06-18" and r["serverInfo"]["name"] == "policy-db"
    assert server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    lst = server.handle(legacy("tools/list", id=2))["result"]
    assert "resultType" not in lst and "ttlMs" not in lst and len(lst["tools"]) == 3
    call = server.handle(legacy("tools/call", {"name": "add", "arguments": {"a": 1, "b": 1}}, id=3))["result"]
    assert call == {"content": [{"type": "text", "text": "2"}], "isError": False}
    old = impl.MCPServer("x", "1").handle(legacy("initialize", {"protocolVersion": "2023-01-01"}))["result"]
    assert old["protocolVersion"] == impl.LEGACY_VERSIONS[0]


@pytest.mark.parametrize("msg,code", [
    ({"jsonrpc": "1.0", "id": 1, "method": "ping"}, -32600),
    ({"jsonrpc": "2.0", "id": 1}, -32600),
])
def test_invalid_requests(server, msg, code):
    assert server.handle(msg)["error"]["code"] == code


def test_unknown_method_and_tool(server):
    assert server.handle(modern("nope"))["error"]["code"] == -32601
    r = server.handle(modern("tools/call", {"name": "zzz", "arguments": {}}))
    assert r["error"]["code"] == -32602 and r["error"]["message"] == "Unknown tool: zzz"
    assert server.handle(modern("tools/call", {"name": "add", "arguments": "x"}))["error"]["code"] == -32602
    assert server.handle(modern("ping"))["result"] == {"resultType": "complete"}


def test_tool_registration_validation(impl):
    s = impl.MCPServer("x", "1")
    with pytest.raises(ValueError):
        s.tool("bad name!", "d", {"type": "object"})
    with pytest.raises(ValueError):
        s.tool("ok", "d", None)


def test_serve_stdio(server):
    lines = [json.dumps(modern("ping", id=1)), "{not json",
             json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
             json.dumps(modern("tools/call", {"name": "add", "arguments": {"a": 1, "b": 1}}, id=2))]
    out = io.StringIO()
    server.serve(io.StringIO("\n".join(lines) + "\n"), out)
    replies = [json.loads(l) for l in out.getvalue().splitlines()]
    assert [r.get("id") for r in replies] == [1, None, 2] and replies[1]["error"]["code"] == -32700


def test_demo_server_subprocess(exercise_dir):
    script = next(p for p in exercise_dir.glob("s*.py"))
    msgs = [modern("server/discover", id=1), modern("tools/list", id=2),
            modern("tools/call", {"name": "lookup_policy", "arguments": {"policy_id": "P-100"}}, id=3),
            modern("tools/call", {"name": "lookup_policy", "arguments": {"policy_id": "X"}}, id=4)]
    proc = subprocess.run([sys.executable, str(script)], input="\n".join(json.dumps(m) for m in msgs) + "\n",
                          capture_output=True, text=True, timeout=20)
    replies = {r["id"]: r for r in (json.loads(l) for l in proc.stdout.splitlines() if l.strip())}
    assert set(replies) == {1, 2, 3, 4}
    assert [t["name"] for t in replies[2]["result"]["tools"]] == ["lookup_policy"]
    assert replies[3]["result"]["structuredContent"] == {"policy_id": "P-100", "status": "active"}
    assert replies[4]["result"]["isError"] is True
