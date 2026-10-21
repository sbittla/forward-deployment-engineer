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
        self._by_key: dict[tuple[str, str], ToolResult] = {}
        self._audit: list[tuple[str, str, str | None, str]] = []

    def register(self, name, description, schema, fn, side_effect=False, roles=None, idempotency_key=None) -> None:
        self._tools[name] = dict(description=description, schema=schema, fn=fn, side_effect=side_effect,
                                 roles=frozenset(roles or ()), key=idempotency_key)

    def specs(self) -> list[dict]:
        return [{"name": n, "description": t["description"], "input_schema": t["schema"]}
                for n, t in self._tools.items()]

    def specs_for(self, role: str) -> list[dict]:
        return [s for s in self.specs() if role in self._tools[s["name"]]["roles"]]

    def audit_log(self) -> tuple:
        return tuple(self._audit)

    def _truncate(self, s: str) -> str:
        if len(s) <= self.max_result_chars:
            return s
        return s[: self.max_result_chars] + f"... [truncated {len(s) - self.max_result_chars} chars]"

    def _record(self, res: ToolResult, name: str, role, outcome: str) -> ToolResult:
        self._audit.append((res.call_id, name, role, outcome))
        return res

    def dispatch(self, call_id: str, name: str, args: dict) -> ToolResult:
        return self._dispatch(call_id, name, args, None)

    def dispatch_as(self, role: str, call_id: str, name: str, args: dict) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None or role not in tool["roles"]:  # deny by default; unknown looks the same as forbidden
            return self._record(ToolResult(call_id, f"Not permitted: {name} for role {role}", True), name, role,
                                "denied")
        return self._dispatch(call_id, name, args, role)

    def _dispatch(self, call_id: str, name: str, args, role) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            res = ToolResult(call_id, f"Unknown tool '{name}'. Available: {', '.join(sorted(self._tools))}", True)
            return self._record(res, name, role, "unknown")
        if tool["side_effect"] and call_id in self._done:
            return self._record(self._done[call_id], name, role, "replayed")
        problems = _problems(tool["schema"], args, "arguments")
        if problems:
            res = ToolResult(call_id, f"Invalid arguments for {name}:\n" + "\n".join(f"- {p}" for p in problems), True)
            return self._record(res, name, role, "invalid")
        key = (name, tool["key"](args)) if tool["side_effect"] and tool["key"] else None
        if key in self._by_key:
            first = self._by_key[key]
            return self._record(ToolResult(call_id, first.content, first.is_error), name, role, "replayed")
        try:
            result = tool["fn"](**args)
        except Exception as exc:
            return self._record(ToolResult(call_id, f"Tool {name} failed: {type(exc).__name__}", True), name, role,
                                "failed")
        content = result if isinstance(result, str) else json.dumps(result, default=str)
        res = ToolResult(call_id, self._truncate(content), False)
        if tool["side_effect"]:
            self._done[call_id] = res
            if key:
                self._by_key[key] = res
        return self._record(res, name, role, "ok")
