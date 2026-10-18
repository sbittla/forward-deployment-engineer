# ex44 · Build an MCP server

**Module:** m08 · **Covers:** R12 MCP & connectors, R11 Tool use · **Time:** 75 min

## Scenario
The customer wants their internal policy database usable from Claude Desktop, Claude Code and their own agent —
without three integrations. The Model Context Protocol (MCP) solves that: build one server, every MCP client can
use it. Production servers usually use an official SDK; building the wire protocol once by hand means you can
debug any MCP integration on a customer site.

## Protocol subset (JSON-RPC 2.0, newline-delimited over stdio)
| Method | Result |
|---|---|
| `initialize` | `{"protocolVersion": <client's if in SUPPORTED_VERSIONS else LATEST>, "capabilities": {"tools": {}}, "serverInfo": {"name", "version"}}` |
| `notifications/initialized` | notification — **no response** |
| `ping` | `{}` |
| `tools/list` | `{"tools": [{"name", "description", "inputSchema"}]}` |
| `tools/call` `{name, arguments}` | `{"content": [{"type": "text", "text": ...}], "isError": bool}` |

Errors (JSON-RPC `error` objects): parse error `-32700`, invalid request `-32600` (not a dict, wrong/missing
`"jsonrpc": "2.0"`, or missing `method`), method not found `-32601`, invalid params `-32602` (unknown tool name or
arguments not a dict). A tool that **raises** is not a protocol error: return a normal result with `isError: true`
and the text `"Error: <message>"`. Any message without an `id` is a notification and never gets a response.

## Your task
`MCPServer(name, version)`:
- `@server.tool(name, description, input_schema)` decorator registers a function called with `**arguments`;
  non-string return values are JSON-encoded.
- `handle(message: dict) -> dict | None` implements the table above.
- `serve(stdin, stdout)` — read lines, parse JSON (bad JSON → `-32700` response with `"id": null`), write each
  response as one JSON line and flush.
- Running the file as a script (`python starter.py`) must start a demo server on real stdin/stdout exposing
  `lookup_policy(policy_id)` that returns `{"policy_id": ..., "status": "active"}` for ids starting with `"P-"`,
  and raises `KeyError` otherwise.
