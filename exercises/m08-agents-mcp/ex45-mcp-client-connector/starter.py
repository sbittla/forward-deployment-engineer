import json
import subprocess
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

    def send(self, msg: dict) -> None:
        raise NotImplementedError

    def recv(self) -> dict:
        raise NotImplementedError


class StdioTransport:
    def __init__(self, cmd: list[str]):
        self.cmd = cmd

    def send(self, msg: dict) -> None:
        raise NotImplementedError

    def recv(self) -> dict:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


MODERN_VERSIONS = ("2026-07-28",)
LEGACY_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
META_VERSION = "io.modelcontextprotocol/protocolVersion"


class MCPClient:
    def __init__(self, transport, name: str = "fde-client", version: str = "0.1"):
        self.transport = transport
        self.name, self.version = name, version
        self.era: str | None = None
        self.protocol_version: str | None = None

    def connect(self) -> dict:
        raise NotImplementedError

    def initialize(self, protocol_version: str = LEGACY_VERSIONS[0]) -> dict:
        raise NotImplementedError

    def list_tools(self) -> list[dict]:
        raise NotImplementedError

    def call_tool(self, name: str, arguments: dict) -> str:
        raise NotImplementedError


@dataclass
class ToolDef:
    name: str
    description: str
    input_schema: dict
    fn: Callable


def make_ticket_tools(conn) -> list[ToolDef]:
    raise NotImplementedError
