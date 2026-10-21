import json
import re
import sys

MODERN_VERSIONS = ("2026-07-28",)
LEGACY_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
META_VERSION = "io.modelcontextprotocol/protocolVersion"
TOOL_NAME = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")


class MCPServer:
    def __init__(self, name: str, version: str, instructions: str = ""):
        self.name = name
        self.version = version
        self.instructions = instructions

    def tool(self, name: str, description: str, input_schema: dict):
        raise NotImplementedError

    def handle(self, message) -> dict | None:
        raise NotImplementedError

    def serve(self, stdin=sys.stdin, stdout=sys.stdout) -> None:
        raise NotImplementedError


if __name__ == "__main__":
    raise NotImplementedError("start the demo server here")
