import json
import subprocess
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


class MCPClient:
    def __init__(self, transport):
        self.transport = transport

    def initialize(self, name: str, version: str, protocol_version: str = "2025-06-18") -> dict:
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
