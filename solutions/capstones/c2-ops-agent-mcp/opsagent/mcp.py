"""MCP (JSON-RPC 2.0) server over the tool registry, plus an in-process client.

The same server can be exposed over stdio to Claude Desktop/Code or another MCP client;
the agent below talks to it through the protocol rather than calling Python functions directly.
"""
import json

PROTOCOL_VERSION = "2025-06-18"


class MCPServer:
    def __init__(self, name: str, registry, version: str = "1.0.0"):
        self.name, self.version, self.registry = name, version, registry

    def handle(self, msg: dict) -> dict | None:
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
            return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "invalid request"}}
        if "id" not in msg:
            return None
        mid, method, params = msg["id"], msg["method"], msg.get("params") or {}

        def ok(result):
            return {"jsonrpc": "2.0", "id": mid, "result": result}

        if method == "initialize":
            return ok({"protocolVersion": PROTOCOL_VERSION, "capabilities": {"tools": {}},
                       "serverInfo": {"name": self.name, "version": self.version}})
        if method == "tools/list":
            return ok({"tools": self.registry.specs()})
        if method == "tools/call":
            text, is_error = self.registry.call(params.get("name"), params.get("arguments", {}))
            return ok({"content": [{"type": "text", "text": text}], "isError": is_error})
        if method == "ping":
            return ok({})
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}

    def serve(self, stdin, stdout):
        for line in stdin:
            if line.strip():
                reply = self.handle(json.loads(line))
                if reply is not None:
                    stdout.write(json.dumps(reply) + "\n")
                    stdout.flush()


class InProcessClient:
    def __init__(self, server: MCPServer):
        self.server = server
        self._id = 0

    def _request(self, method, params=None):
        self._id += 1
        reply = self.server.handle({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}})
        if "error" in reply:
            raise RuntimeError(reply["error"]["message"])
        return reply["result"]

    def initialize(self) -> dict:
        info = self._request("initialize", {"protocolVersion": PROTOCOL_VERSION, "capabilities": {},
                                            "clientInfo": {"name": "opsagent", "version": "1.0.0"}})
        self.server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return info

    def list_tools(self) -> list[dict]:
        return self._request("tools/list")["tools"]

    def call_tool(self, name: str, arguments: dict) -> tuple[str, bool]:
        result = self._request("tools/call", {"name": name, "arguments": arguments})
        return "".join(c["text"] for c in result["content"] if c["type"] == "text"), result["isError"]
