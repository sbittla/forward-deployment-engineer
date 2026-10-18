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
        raise NotImplementedError

    def serve(self, stdin, stdout):
        raise NotImplementedError


class InProcessClient:
    def __init__(self, server: MCPServer):
        self.server = server
        self._id = 0

    def _request(self, method, params=None):
        raise NotImplementedError

    def connect(self) -> dict:
        raise NotImplementedError

    def list_tools(self) -> list[dict]:
        raise NotImplementedError

    def call_tool(self, name: str, arguments: dict) -> tuple[str, bool]:
        raise NotImplementedError
