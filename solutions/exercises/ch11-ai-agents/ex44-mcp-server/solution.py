"""Dual-era MCP server: stateless 2026-07-28 requests, plus the legacy initialize handshake for older clients."""
import json
import re
import sys

MODERN_VERSIONS = ("2026-07-28",)
LEGACY_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
META_VERSION = "io.modelcontextprotocol/protocolVersion"
SERVER_INFO = "io.modelcontextprotocol/serverInfo"
TOOL_NAME = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")

PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS, UNSUPPORTED_VERSION = -32700, -32600, -32601, -32602, -32022


def _error(id_, code, message, data=None):
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": id_, "error": err}


class MCPServer:
    def __init__(self, name: str, version: str, instructions: str = ""):
        self.name = name
        self.version = version
        self.instructions = instructions
        self._tools: dict[str, dict] = {}
        self._legacy_version: str | None = None   # set by an initialize request (stdio: process-scoped)

    def tool(self, name: str, description: str, input_schema: dict):
        if not TOOL_NAME.match(name):
            raise ValueError(f"invalid tool name {name!r}")
        if not isinstance(input_schema, dict):
            raise ValueError("inputSchema must be a JSON Schema object")

        def deco(fn):
            self._tools[name] = {"description": description, "inputSchema": input_schema, "fn": fn}
            return fn
        return deco

    # ---------- shared method implementations ----------

    def _tools_list(self):
        return {"tools": [{"name": n, "description": t["description"], "inputSchema": t["inputSchema"]}
                          for n, t in self._tools.items()]}

    def _tools_call(self, id_, params):
        name, args = params.get("name"), params.get("arguments", {})
        if name not in self._tools:
            return None, _error(id_, INVALID_PARAMS, f"Unknown tool: {name}")
        if not isinstance(args, dict):
            return None, _error(id_, INVALID_PARAMS, "arguments must be an object")
        try:
            out = self._tools[name]["fn"](**args)
        except Exception as exc:  # tool failures are results the model can read and recover from
            msg = exc.args[0] if isinstance(exc, KeyError) and exc.args else str(exc)
            return {"content": [{"type": "text", "text": f"Error: {msg}"}], "isError": True}, None
        if isinstance(out, dict):     # MCP's structuredContent must be a JSON object
            return {"content": [{"type": "text", "text": json.dumps(out)}], "structuredContent": out,
                    "isError": False}, None
        if isinstance(out, list):
            return {"content": [{"type": "text", "text": json.dumps(out)}], "isError": False}, None
        return {"content": [{"type": "text", "text": str(out)}], "isError": False}, None

    # ---------- dispatch ----------

    def handle(self, message) -> dict | None:
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or "method" not in message:
            return _error(message.get("id") if isinstance(message, dict) else None, INVALID_REQUEST, "invalid request")
        if "id" not in message:
            return None  # notifications never get a response
        id_, method = message["id"], message["method"]
        params = message.get("params") or {}
        version = (params.get("_meta") or {}).get(META_VERSION)

        if method == "initialize":
            requested = params.get("protocolVersion")
            self._legacy_version = requested if requested in LEGACY_VERSIONS else LEGACY_VERSIONS[0]
            return {"jsonrpc": "2.0", "id": id_, "result": {
                "protocolVersion": self._legacy_version, "capabilities": {"tools": {}},
                "serverInfo": {"name": self.name, "version": self.version}}}

        if version is None:
            if self._legacy_version is None:
                return _error(id_, INVALID_PARAMS, f"missing _meta['{META_VERSION}'] (or legacy initialize first)")
            return self._dispatch(id_, method, params, modern=False)
        if version not in MODERN_VERSIONS:
            return _error(id_, UNSUPPORTED_VERSION, "Unsupported protocol version",
                          {"supported": list(MODERN_VERSIONS + LEGACY_VERSIONS), "requested": version})
        return self._dispatch(id_, method, params, modern=True)

    def _dispatch(self, id_, method, params, modern: bool):
        def ok(result):
            if modern:
                result = {"resultType": "complete", **result}
            return {"jsonrpc": "2.0", "id": id_, "result": result}

        if method == "server/discover" and modern:
            return ok({"supportedVersions": list(MODERN_VERSIONS), "capabilities": {"tools": {}},
                       "_meta": {SERVER_INFO: {"name": self.name, "version": self.version}},
                       "instructions": self.instructions, "ttlMs": 3600000})
        if method == "ping":
            return ok({})
        if method == "tools/list":
            result = self._tools_list()
            if modern:
                result["ttlMs"] = 300000
            return ok(result)
        if method == "tools/call":
            result, err = self._tools_call(id_, params)
            return err or ok(result)
        return _error(id_, METHOD_NOT_FOUND, f"method not found: {method}")

    def serve(self, stdin=sys.stdin, stdout=sys.stdout) -> None:
        for line in stdin:
            if not line.strip():
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                reply = _error(None, PARSE_ERROR, "parse error")
            else:
                reply = self.handle(msg)
            if reply is not None:
                stdout.write(json.dumps(reply) + "\n")
                stdout.flush()


def demo_server() -> MCPServer:
    server = MCPServer("policy-db", "0.2.0", instructions="Look up insurance policies by id (e.g. P-100).")

    @server.tool("lookup_policy", "Look up a policy by id (e.g. P-100).",
                 {"type": "object", "required": ["policy_id"], "properties": {"policy_id": {"type": "string"}}})
    def lookup_policy(policy_id):
        if not policy_id.startswith("P-"):
            raise KeyError(f"policy {policy_id} not found")
        return {"policy_id": policy_id, "status": "active"}

    return server


if __name__ == "__main__":
    demo_server().serve()
