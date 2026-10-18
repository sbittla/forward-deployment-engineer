import json
import subprocess
from collections import deque
from dataclasses import dataclass
from typing import Callable


class RPCError(Exception):
    def __init__(self, code: int, message: str, data=None):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.data = data


class ToolError(Exception):
    pass


class InProcessTransport:
    def __init__(self, handler: Callable[[dict], dict | None]):
        self.handler = handler
        self._replies: deque = deque()

    def send(self, msg: dict) -> None:
        reply = self.handler(msg)
        if reply is not None:
            self._replies.append(reply)

    def recv(self) -> dict:
        if not self._replies:
            raise EOFError("no pending replies")
        return self._replies.popleft()


class StdioTransport:
    def __init__(self, cmd: list[str]):
        self.cmd = cmd
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)

    def send(self, msg: dict) -> None:
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()

    def recv(self) -> dict:
        line = self.proc.stdout.readline()
        if not line:
            raise EOFError("server closed stdout")
        return json.loads(line)

    def close(self) -> None:
        if self.proc.poll() is None:
            self.proc.stdin.close()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.proc.stdout.close()


MODERN_VERSIONS = ("2026-07-28",)
LEGACY_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
META_VERSION = "io.modelcontextprotocol/protocolVersion"
UNSUPPORTED_VERSION = -32022


class MCPClient:
    """Dual-era client: probes server/discover (2026-07-28) and falls back to the legacy initialize handshake."""

    def __init__(self, transport, name: str = "fde-client", version: str = "0.1"):
        self.transport = transport
        self.name, self.version = name, version
        self.era: str | None = None
        self.protocol_version: str | None = None
        self._next_id = 1

    def _meta(self) -> dict:
        return {META_VERSION: self.protocol_version,
                "io.modelcontextprotocol/clientInfo": {"name": self.name, "version": self.version},
                "io.modelcontextprotocol/clientCapabilities": {}}

    def _request(self, method: str, params: dict | None = None):
        mid = self._next_id
        self._next_id += 1
        if self.era == "modern":
            params = {**(params or {}), "_meta": self._meta()}
        msg = {"jsonrpc": "2.0", "id": mid, "method": method}
        if params is not None:
            msg["params"] = params
        self.transport.send(msg)
        while True:
            reply = self.transport.recv()
            if reply.get("id") != mid:
                continue  # notification or unrelated message
            if "error" in reply:
                err = reply["error"]
                raise RPCError(err["code"], err.get("message", ""), err.get("data"))
            return reply["result"]

    def connect(self) -> dict:
        """Negotiate an era once per connection; returns {era, protocolVersion, serverInfo, capabilities}."""
        self.era, self.protocol_version = "modern", MODERN_VERSIONS[0]
        try:
            r = self._request("server/discover")
        except RPCError as exc:
            supported = (exc.data or {}).get("supported", []) if exc.code == UNSUPPORTED_VERSION else []
            modern = [v for v in MODERN_VERSIONS if v in supported]
            if modern:  # the server speaks a different modern revision we also know
                self.protocol_version = modern[0]
                r = self._request("server/discover")
            else:
                legacy = [v for v in LEGACY_VERSIONS if v in supported]
                result = self.initialize(legacy[0] if legacy else LEGACY_VERSIONS[0])
                return {"era": "legacy", "protocolVersion": result["protocolVersion"],
                        "serverInfo": result.get("serverInfo", {}), "capabilities": result.get("capabilities", {})}
        return {"era": "modern", "protocolVersion": self.protocol_version,
                "serverInfo": r.get("_meta", {}).get("io.modelcontextprotocol/serverInfo", {}),
                "capabilities": r.get("capabilities", {})}

    def initialize(self, protocol_version: str = LEGACY_VERSIONS[0]) -> dict:
        self.era, self.protocol_version = "legacy", protocol_version
        result = self._request("initialize", {"protocolVersion": protocol_version, "capabilities": {},
                                              "clientInfo": {"name": self.name, "version": self.version}})
        self.protocol_version = result.get("protocolVersion", protocol_version)
        self.transport.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return result

    def list_tools(self) -> list[dict]:
        return self._request("tools/list")["tools"]

    def call_tool(self, name: str, arguments: dict) -> str:
        result = self._request("tools/call", {"name": name, "arguments": arguments})
        text = "".join(c.get("text", "") for c in result.get("content", []) if c.get("type") == "text")
        if result.get("isError"):
            raise ToolError(text)
        return text


@dataclass
class ToolDef:
    name: str
    description: str
    input_schema: dict
    fn: Callable


def make_ticket_tools(conn) -> list[ToolDef]:
    def search_tickets(query: str, status: str | None = None, limit: int = 10):
        if not 1 <= int(limit) <= 50:
            raise ValueError("limit must be between 1 and 50")
        sql = "SELECT id, title, status FROM tickets WHERE lower(title) LIKE ? "
        args: list = [f"%{query.lower()}%"]
        if status is not None:
            sql += "AND status = ? "
            args.append(status)
        sql += "ORDER BY id LIMIT ?"
        args.append(int(limit))
        return [{"id": r[0], "title": r[1], "status": r[2]} for r in conn.execute(sql, args)]

    def get_ticket(ticket_id: int):
        cur = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        row = cur.fetchone()
        if row is None:
            raise KeyError(f"ticket {ticket_id} not found")
        return dict(zip([d[0] for d in cur.description], row))

    return [
        ToolDef("search_tickets", "Search tickets by title text, optionally filtered by status.",
                {"type": "object", "required": ["query"], "properties": {
                    "query": {"type": "string"}, "status": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 50}}}, search_tickets),
        ToolDef("get_ticket", "Fetch one ticket by id.",
                {"type": "object", "required": ["ticket_id"], "properties": {"ticket_id": {"type": "integer"}}},
                get_ticket),
    ]
