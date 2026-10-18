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
        raise NotImplementedError

    def serve(self, stdin, stdout):
        raise NotImplementedError


class InProcessClient:
    def __init__(self, server: MCPServer):
        self.server = server
        self._id = 0

    def _request(self, method, params=None):
        raise NotImplementedError

    def initialize(self) -> dict:
        raise NotImplementedError

    def list_tools(self) -> list[dict]:
        raise NotImplementedError

    def call_tool(self, name: str, arguments: dict) -> tuple[str, bool]:
        raise NotImplementedError
