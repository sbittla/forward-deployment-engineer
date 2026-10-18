import json
import sys

SUPPORTED_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
LATEST = SUPPORTED_VERSIONS[0]


class MCPServer:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version

    def tool(self, name: str, description: str, input_schema: dict):
        raise NotImplementedError

    def handle(self, message) -> dict | None:
        raise NotImplementedError

    def serve(self, stdin=sys.stdin, stdout=sys.stdout) -> None:
        raise NotImplementedError


if __name__ == "__main__":
    raise NotImplementedError("start the demo server here")
