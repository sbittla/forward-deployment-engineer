"""MCP (JSON-RPC 2.0) server over the tool registry, plus an in-process client.

Speaks MCP 2026-07-28 (stateless: every request carries its protocol version in `_meta`, discovery via
`server/discover`) and still answers the legacy `initialize` handshake for clients on 2025-11-25 and earlier.
The same server can be exposed over stdio to Claude Desktop/Code or another MCP client;
the agent talks to it through the protocol rather than calling Python functions directly.
"""
import json

MODERN_VERSIONS = ("2026-07-28",)
LEGACY_VERSIONS = ("2025-11-25", "2025-06-18")
PROTOCOL_VERSION = MODERN_VERSIONS[0]
META_VERSION = "io.modelcontextprotocol/protocolVersion"
SERVER_INFO = "io.modelcontextprotocol/serverInfo"


class MCPServer:
    def __init__(self, name: str, registry, version: str = "1.0.0"):
        self.name, self.version, self.registry = name, version, registry
        self._legacy = False

    def handle(self, msg: dict) -> dict | None:
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
            return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "invalid request"}}
        if "id" not in msg:
            return None
        mid, method, params = msg["id"], msg["method"], msg.get("params") or {}
        version = (params.get("_meta") or {}).get(META_VERSION)

        def error(code, message, data=None):
            err = {"code": code, "message": message}
            if data is not None:
                err["data"] = data
            return {"jsonrpc": "2.0", "id": mid, "error": err}

        if method == "initialize":
            self._legacy = True
            requested = params.get("protocolVersion")
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "protocolVersion": requested if requested in LEGACY_VERSIONS else LEGACY_VERSIONS[0],
                "capabilities": {"tools": {}}, "serverInfo": {"name": self.name, "version": self.version}}}
        if version is None and not self._legacy:
            return error(-32602, f"missing _meta['{META_VERSION}']")
        if version is not None and version not in MODERN_VERSIONS:
            return error(-32022, "Unsupported protocol version",
                         {"supported": list(MODERN_VERSIONS + LEGACY_VERSIONS), "requested": version})
        modern = version is not None

        def ok(result):
            return {"jsonrpc": "2.0", "id": mid, "result": {"resultType": "complete", **result} if modern else result}

        if method == "server/discover" and modern:
            return ok({"supportedVersions": list(MODERN_VERSIONS), "capabilities": {"tools": {}},
                       "_meta": {SERVER_INFO: {"name": self.name, "version": self.version}}, "ttlMs": 3600000})
        if method == "tools/list":
            return ok({"tools": self.registry.specs(), **({"ttlMs": 300000} if modern else {})})
        if method == "tools/call":
            text, is_error = self.registry.call(params.get("name"), params.get("arguments", {}))
            return ok({"content": [{"type": "text", "text": text}], "isError": is_error})
        if method == "ping":
            return ok({})
        return error(-32601, f"method not found: {method}")

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
        params = {**(params or {}), "_meta": {META_VERSION: PROTOCOL_VERSION,
                                              "io.modelcontextprotocol/clientInfo": {"name": "opsagent", "version": "1.0.0"},
                                              "io.modelcontextprotocol/clientCapabilities": {}}}
        reply = self.server.handle({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params})
        if "error" in reply:
            raise RuntimeError(reply["error"]["message"])
        return reply["result"]

    def connect(self) -> dict:
        result = self._request("server/discover")
        return {"protocolVersion": PROTOCOL_VERSION, "capabilities": result["capabilities"],
                "serverInfo": result["_meta"][SERVER_INFO]}

    def list_tools(self) -> list[dict]:
        return self._request("tools/list")["tools"]

    def call_tool(self, name: str, arguments: dict) -> tuple[str, bool]:
        result = self._request("tools/call", {"name": name, "arguments": arguments})
        return "".join(c["text"] for c in result["content"] if c["type"] == "text"), result["isError"]
