# ex45 hints · MCP client and database connector

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Start with the connector (`make_ticket_tools`). It's plain SQL and is tested in isolation. Then write
`InProcessTransport` (a queue of replies) and one `_request(method, params)` method on the client. Every client call
goes through `_request`: assign the next id, add `_meta` if the era is modern, send, and wait for the matching reply.
</details>

<details>
<summary>Hint 2 · The approach</summary>

`connect()`:

1. Set the era to modern and try `server/discover`.
2. On `RPCError` with code -32022, read `error.data.supported`. If it shares a modern version, rediscover with it;
   otherwise call `initialize` with the first shared legacy version.
3. On any other `RPCError` (old servers answer -32601), call `initialize("2025-11-25")`.

`initialize` sets the era to legacy, sends the request without `_meta`, then sends `notifications/initialized` with
no `id` and doesn't wait for a reply.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- In `_request`, loop over `recv()` and **skip** any message whose `id` doesn't match. The stdio test server sends a
  notification before every reply.
- Keep `data` on `RPCError`. The version fallback depends on it.
- `call_tool` joins the text of every `text` content item, then raises `ToolError` if `isError` is true.
- Connector SQL: use `LIKE ?` with `f"%{query.lower()}%"` against `lower(title)`, and bind `status` and `limit` as
  parameters too. The injection test passes because nothing is ever formatted into the SQL string.
- `StdioTransport` needs `text=True`, a flush after every write, and `readline()` returning `""` treated as EOF.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_connector_tools` | Case-sensitive search; limit not validated; query formatted into the SQL; missing ticket returns `None` |
| `test_client_modern_server` | `_meta` missing on later requests; `serverInfo` read from the wrong place; ids not sequential |
| `test_client_falls_back_to_legacy` | No fallback on -32601; `_meta` still sent in the legacy era; `initialized` sent with an id |
| `test_unsupported_version_picks_from_server_list` | `error.data.supported` ignored, so the default legacy version is used |
| `test_rpc_error_keeps_data` | `RPCError` doesn't store `code` and `data` as attributes |
| `test_client_stdio` | Notifications not skipped; no flush after writing; content items not joined |
