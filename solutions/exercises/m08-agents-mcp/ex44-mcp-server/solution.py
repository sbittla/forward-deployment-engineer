import json
import sys

SUPPORTED_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
LATEST = SUPPORTED_VERSIONS[0]

PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS = -32700, -32600, -32601, -32602


def _error(id_, code, message):
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}


def _result(id_, result):
    return {"jsonrpc": "2.0", "id": id_, "result": result}


class MCPServer:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self._tools: dict[str, dict] = {}

    def tool(self, name: str, description: str, input_schema: dict):
        def deco(fn):
            self._tools[name] = {"description": description, "inputSchema": input_schema, "fn": fn}
            return fn
        return deco

    def _call_tool(self, id_, params):
        name, args = params.get("name"), params.get("arguments", {})
        if name not in self._tools:
            return _error(id_, INVALID_PARAMS, f"unknown tool: {name}")
        if not isinstance(args, dict):
            return _error(id_, INVALID_PARAMS, "arguments must be an object")
        try:
            out = self._tools[name]["fn"](**args)
            text, is_error = (out if isinstance(out, str) else json.dumps(out, default=str)), False
        except Exception as exc:  # tool failures are results the model can read, not protocol errors
            msg = exc.args[0] if isinstance(exc, KeyError) and exc.args else str(exc)
            text, is_error = f"Error: {msg}", True
        return _result(id_, {"content": [{"type": "text", "text": text}], "isError": is_error})

    def handle(self, message) -> dict | None:
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or "method" not in message:
            return _error(message.get("id") if isinstance(message, dict) else None, INVALID_REQUEST, "invalid request")
        if "id" not in message:
            return None  # notification
        id_, method, params = message["id"], message["method"], message.get("params") or {}
        if method == "initialize":
            requested = params.get("protocolVersion")
            return _result(id_, {
                "protocolVersion": requested if requested in SUPPORTED_VERSIONS else LATEST,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": self.name, "version": self.version},
            })
        if method == "ping":
            return _result(id_, {})
        if method == "tools/list":
            return _result(id_, {"tools": [{"name": n, "description": t["description"], "inputSchema": t["inputSchema"]}
                                           for n, t in self._tools.items()]})
        if method == "tools/call":
            return self._call_tool(id_, params)
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
    server = MCPServer("policy-db", "0.1.0")

    @server.tool("lookup_policy", "Look up a policy by id (e.g. P-100).",
                 {"type": "object", "required": ["policy_id"], "properties": {"policy_id": {"type": "string"}}})
    def lookup_policy(policy_id):
        if not policy_id.startswith("P-"):
            raise KeyError(f"policy {policy_id} not found")
        return {"policy_id": policy_id, "status": "active"}

    return server


if __name__ == "__main__":
    demo_server().serve()
