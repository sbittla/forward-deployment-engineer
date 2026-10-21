from dataclasses import dataclass


@dataclass
class ToolResult:
    call_id: str
    content: str
    is_error: bool


class ToolRegistry:
    def __init__(self, max_result_chars: int = 2000):
        self.max_result_chars = max_result_chars

    def register(self, name, description, schema, fn, side_effect=False, roles=None, idempotency_key=None) -> None:
        raise NotImplementedError

    def specs(self) -> list[dict]:
        raise NotImplementedError

    def specs_for(self, role: str) -> list[dict]:
        raise NotImplementedError

    def dispatch(self, call_id: str, name: str, args: dict) -> ToolResult:
        raise NotImplementedError

    def dispatch_as(self, role: str, call_id: str, name: str, args: dict) -> ToolResult:
        raise NotImplementedError

    def audit_log(self) -> tuple:
        raise NotImplementedError
