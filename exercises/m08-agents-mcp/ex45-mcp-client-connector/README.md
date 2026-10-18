# ex45 · MCP client and database connector

**Module:** m08 · **Covers:** R12 MCP & connectors, R05 System integration · **Time:** 60 min

## Scenario
You are wiring the customer's ticket database into their agent platform as an MCP connector, and you need a
client to smoke-test any MCP server on site (theirs or yours) without installing a desktop app.

## Your task
**Client**
- `InProcessTransport(handler)` — `send(msg)` calls `handler(msg)` and queues any non-None reply; `recv()` pops the
  next reply (raise `EOFError` if none).
- `StdioTransport(cmd: list[str])` — starts the server process; `send` writes one JSON line and flushes; `recv`
  reads one line (`EOFError` on EOF); `close()` terminates the process.
- `MCPClient(transport)`:
  - `initialize(name, version, protocol_version="2025-06-18") -> dict` — sends `initialize` with
    `{"protocolVersion", "capabilities": {}, "clientInfo": {"name", "version"}}`, returns the result, then sends the
    `notifications/initialized` notification (no `id`).
  - `list_tools() -> list[dict]` and `call_tool(name, arguments) -> str` (joined text of all `text` content items).
  - request ids start at 1 and increment; while waiting for a reply, skip messages whose `id` doesn't match
    (servers may send notifications).
  - JSON-RPC `error` → raise `RPCError(code, message)`; a result with `isError: true` → raise `ToolError(text)`.

**Connector**
- `make_ticket_tools(conn) -> list[ToolDef]` with `ToolDef(name, description, input_schema, fn)`:
  - `search_tickets(query, status=None, limit=10)` → list of `{"id","title","status"}` whose title contains
    `query` (case-insensitive), optional exact `status` filter, ordered by id, **parameterised SQL only**;
    `limit` must be 1–50 else `ValueError`.
  - `get_ticket(ticket_id)` → full row as dict, or `KeyError` if absent.
