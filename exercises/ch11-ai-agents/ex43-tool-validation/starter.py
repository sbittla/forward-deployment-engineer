from dataclasses import dataclass


@dataclass
class ToolResult:
    call_id: str
    content: str
    is_error: bool


class ToolRegistry:
    def __init__(self, max_result_chars: int = 2000):
        self.max_result_chars = max_result_chars

    def register(self, name, description, schema, fn, side_effect=False) -> None:
        raise NotImplementedError

    def specs(self) -> list[dict]:
        raise NotImplementedError

    def dispatch(self, call_id: str, name: str, args: dict) -> ToolResult:
        raise NotImplementedError
