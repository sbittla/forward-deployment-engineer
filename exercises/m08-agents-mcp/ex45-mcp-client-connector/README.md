# ex45 · MCP client and database connector

**Module:** m08 · **Covers:** R12 MCP & connectors, R05 System integration · **Time:** 75 min · **As of:** MCP spec 2026-07-28

## Learning objectives
- Negotiate the protocol era with an unknown MCP server and degrade gracefully.
- Keep protocol errors (`RPCError`) and tool failures (`ToolError`) distinct in client code.
- Expose a database safely as tools: parameterised SQL, bounded limits, typed schemas.

## Scenario
You are wiring the customer's ticket database into their agent platform as an MCP connector, and you need a
client to smoke-test any MCP server on site (theirs or yours) without installing a desktop app.

## Your task
**Client**
- `InProcessTransport(handler)` — `send(msg)` calls `handler(msg)` and queues any non-None reply; `recv()` pops the
  next reply (raise `EOFError` if none).
- `StdioTransport(cmd: list[str])` — starts the server process; `send` writes one JSON line and flushes; `recv`
  reads one line (`EOFError` on EOF); `close()` terminates the process.
- `MCPClient(transport, name="fde-client", version="0.1")` is **dual-era** (MCP spec 2026-07-28 plus legacy):
  - `connect() -> {"era", "protocolVersion", "serverInfo", "capabilities"}` probes `server/discover` with
    `params._meta` = `{"io.modelcontextprotocol/protocolVersion": "2026-07-28", ".../clientInfo": {name, version},
    ".../clientCapabilities": {}}`. On success, set `era = "modern"`; `serverInfo` comes from
    `result._meta["io.modelcontextprotocol/serverInfo"]`.
  - On a `-32022` error, read `error.data.supported`: retry discovery with a modern version you share, otherwise
    `initialize` with the first shared legacy version. On any other error (old servers answer `-32601`), fall back to
    `initialize("2025-11-25")`. Either fallback sets `era = "legacy"`.
  - `initialize(protocol_version="2025-11-25") -> dict` sends `initialize` with `{"protocolVersion", "capabilities": {},
    "clientInfo": {"name", "version"}}`, returns the result, then sends `notifications/initialized` (no `id`).
  - In the modern era every request carries the `_meta` block; in the legacy era none does.
  - `list_tools() -> list[dict]` and `call_tool(name, arguments) -> str` (joined text of all `text` content items).
  - Request ids start at 1 and increment; while waiting for a reply, skip messages whose `id` doesn't match
    (servers may send notifications).
  - JSON-RPC `error` → raise `RPCError(code, message, data)`; a result with `isError: true` → raise `ToolError(text)`.

**Connector**
- `make_ticket_tools(conn) -> list[ToolDef]` with `ToolDef(name, description, input_schema, fn)`:
  - `search_tickets(query, status=None, limit=10)` → list of `{"id","title","status"}` whose title contains
    `query` (case-insensitive), optional exact `status` filter, ordered by id, **parameterised SQL only**;
    `limit` must be 1–50 else `ValueError`.
  - `get_ticket(ticket_id)` → full row as dict, or `KeyError` if absent.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "MCP client and database connector".
Before I write code, teach me MCP client responsibilities: discovery, era negotiation and fallback, request ids,
skipping notifications, and designing safe database tools. Use short Python examples that are not the exercise
solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get
one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m08-agents-mcp/ex45-mcp-client-connector/starter.py so that test_mcp_client.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `RPCError`,
`ToolError`, `InProcessTransport`, `StdioTransport`, `MCPClient`, `ToolDef`, `make_ticket_tools`. Constraints:
Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses
YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m08-agents-mcp/ex45-mcp-client-connector` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "MCP client and database connector" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Does the client ever send _meta to a legacy server, or omit it for a modern one?
Can a malicious query string escape parameterisation? What happens when the server sends a notification mid-request?
Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
