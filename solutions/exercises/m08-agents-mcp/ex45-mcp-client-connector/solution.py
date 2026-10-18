import json
import subprocess
from collections import deque
from dataclasses import dataclass
from typing import Callable


class RPCError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


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


class MCPClient:
    def __init__(self, transport):
        self.transport = transport
        self._next_id = 1

    def _request(self, method: str, params: dict | None = None):
        mid = self._next_id
        self._next_id += 1
        msg = {"jsonrpc": "2.0", "id": mid, "method": method}
        if params is not None:
            msg["params"] = params
        self.transport.send(msg)
        while True:
            reply = self.transport.recv()
            if reply.get("id") != mid:
                continue  # notification or unrelated message
            if "error" in reply:
                raise RPCError(reply["error"]["code"], reply["error"].get("message", ""))
            return reply["result"]

    def initialize(self, name: str, version: str, protocol_version: str = "2025-06-18") -> dict:
        result = self._request("initialize", {"protocolVersion": protocol_version, "capabilities": {},
                                              "clientInfo": {"name": name, "version": version}})
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
