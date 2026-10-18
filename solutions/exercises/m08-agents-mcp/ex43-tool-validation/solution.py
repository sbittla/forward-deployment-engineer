import json
from dataclasses import dataclass

TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
}


@dataclass
class ToolResult:
    call_id: str
    content: str
    is_error: bool


def _problems(schema: dict, value, path: str) -> list[str]:
    t = schema.get("type")
    if t and not TYPES[t](value):
        return [f"{path} must be a {t} (got {type(value).__name__} {value!r})"]
    out = []
    if "enum" in schema and value not in schema["enum"]:
        out.append(f"{path} must be one of {schema['enum']} (got {value!r})")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            out.append(f"{path} must be >= {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            out.append(f"{path} must be <= {schema['maximum']}")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        out += [f"{k} is required" for k in schema.get("required", []) if k not in value]
        for k, v in value.items():
            if k in props:
                out += _problems(props[k], v, k)
            elif schema.get("additionalProperties") is False:
                out.append(f"{k} is not an allowed argument")
    return out


class ToolRegistry:
    def __init__(self, max_result_chars: int = 2000):
        self.max_result_chars = max_result_chars
        self._tools: dict[str, dict] = {}
        self._done: dict[str, ToolResult] = {}

    def register(self, name, description, schema, fn, side_effect=False) -> None:
        self._tools[name] = dict(description=description, schema=schema, fn=fn, side_effect=side_effect)

    def specs(self) -> list[dict]:
        return [{"name": n, "description": t["description"], "input_schema": t["schema"]}
                for n, t in self._tools.items()]

    def _truncate(self, s: str) -> str:
        if len(s) <= self.max_result_chars:
            return s
        return s[: self.max_result_chars] + f"... [truncated {len(s) - self.max_result_chars} chars]"

    def dispatch(self, call_id: str, name: str, args: dict) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(call_id, f"Unknown tool '{name}'. Available: {', '.join(sorted(self._tools))}", True)
        if tool["side_effect"] and call_id in self._done:
            return self._done[call_id]
        problems = _problems(tool["schema"], args, "arguments")
        if problems:
            return ToolResult(call_id, f"Invalid arguments for {name}:\n" + "\n".join(f"- {p}" for p in problems), True)
        try:
            result = tool["fn"](**args)
        except Exception as exc:
            return ToolResult(call_id, f"Tool {name} failed: {type(exc).__name__}", True)
        content = result if isinstance(result, str) else json.dumps(result, default=str)
        res = ToolResult(call_id, self._truncate(content), False)
        if tool["side_effect"]:
            self._done[call_id] = res
        return res
