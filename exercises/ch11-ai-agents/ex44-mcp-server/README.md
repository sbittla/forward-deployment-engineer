# ex44 · Build an MCP server (spec 2026-07-28, dual-era)

**Chapter:** 11 · AI Agents (`exercises/ch11-ai-agents/`) · **Covers:** R12 MCP & connectors, R11 Tool use · **As of:** MCP spec 2026-07-28

## Learning objectives
- Implement the current, stateless MCP request model and the mandatory `server/discover` RPC.
- Negotiate protocol versions per request and stay interoperable with handshake-based (legacy) clients.
- Separate protocol errors from tool execution errors so models can self-correct.

## Scenario
The customer wants their internal policy database usable from Claude Desktop, Claude Code and their own agent
without three integrations. MCP solves that. The protocol changed in **2026-07-28**: the `initialize` handshake is
gone, and every request carries its own protocol version, so servers are stateless and load-balance freely. Customers
still run older clients, though, so your server must be **dual-era**. Production servers normally use an official
SDK; building the wire protocol once by hand means you can debug any integration on site.

## Protocol you implement (JSON-RPC 2.0, newline-delimited over stdio)
**Modern requests** (2026-07-28) carry `params._meta["io.modelcontextprotocol/protocolVersion"]` (plus
`.../clientInfo` and `.../clientCapabilities`). Every modern result includes `"resultType": "complete"`.

| Method | Result |
|---|---|
| `server/discover` | `{"resultType", "supportedVersions": MODERN_VERSIONS, "capabilities": {"tools": {}}, "_meta": {"io.modelcontextprotocol/serverInfo": {"name", "version"}}, "instructions", "ttlMs": 3600000}` |
| `tools/list` | `{"resultType", "tools": [{"name", "description", "inputSchema"}...] (registration order), "ttlMs": 300000}` |
| `tools/call` `{name, arguments}` | `{"resultType", "content": [{"type": "text", "text"}], "isError": bool}`; when the tool returns a dict or list, also `"structuredContent"` with the value and the JSON text in `content` |
| `ping` | `{"resultType": "complete"}` |

**Legacy requests** (`2025-11-25` and earlier): an `initialize` request returns `{"protocolVersion": <client's
if in LEGACY_VERSIONS else LEGACY_VERSIONS[0]>, "capabilities": {"tools": {}}, "serverInfo": {...}}` and switches
this server process into legacy mode. After that, requests **without** `_meta` are served with legacy result shapes
(no `resultType`, no `ttlMs`). `notifications/initialized` and any other message without an `id` gets no response.

**Errors**
| Condition | Error |
|---|---|
| Modern request with a version not in `MODERN_VERSIONS` | `-32022` `"Unsupported protocol version"`, `data = {"supported": MODERN_VERSIONS + LEGACY_VERSIONS, "requested": ...}` |
| Request without `_meta` version and no legacy `initialize` seen | `-32602` (message names the missing `_meta` key) |
| Not a dict, `jsonrpc != "2.0"`, or no `method` | `-32600` |
| Unknown method | `-32601` |
| Unknown tool, or `arguments` not an object | `-32602` (`"Unknown tool: <name>"`) |
| Tool raises | **not** a protocol error: result with `isError: true` and text `"Error: <message>"` |
| Bad JSON on the wire (`serve`) | `-32700` with `"id": null` |

## Your task
- `MCPServer(name, version, instructions="")` with `@server.tool(name, description, input_schema)`. Reject tool names
  that don't match `^[A-Za-z0-9_.-]{1,128}$` and schemas that aren't dicts (`ValueError`).
- `handle(message) -> dict | None` implementing the tables above; `serve(stdin, stdout)` for stdio.
- Running the file as a script starts a demo server exposing `lookup_policy(policy_id)`, which returns
  `{"policy_id": ..., "status": "active"}` for ids starting with `P-` and raises `KeyError` otherwise.

## Field notes
When a customer's MCP integration "just stopped working" after a client upgrade, check the era first: a legacy-only
server facing a modern client fails silently or with an obscure error. Dual-era servers buy you a migration window.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Build an MCP server (spec
2026-07-28, dual-era)". Before I write code, teach me the Model Context Protocol: JSON-RPC 2.0 framing over stdio,
the 2026-07-28 changes (per-request _meta protocol version, server/discover, -32022 UnsupportedProtocolVersionError,
resultType, ttlMs), and how dual-era servers keep legacy initialize clients working. Use short Python examples that
are not the exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me
what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch11-ai-agents/ex44-mcp-server/starter.py so that test_mcp_server.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `MCPServer`.
Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the
README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch11-ai-agents/ex44-mcp-server` and show me the output. If the README and the tests disagree, stop and
tell me instead of guessing.
```
**Review**
```text
Review my solution to "Build an MCP server (spec 2026-07-28, dual-era)" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Does a modern request with an unsupported version always return -32022
with supported and requested? Can a legacy initialize change behaviour for modern requests? Are notifications ever
answered? Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
