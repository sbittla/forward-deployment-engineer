# ex44 hints · Build an MCP server (spec 2026-07-28, dual-era)

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write a `_error(id, code, message, data=None)` helper that builds a JSON-RPC error object, then get `ping` working in
the modern era. That one method makes you write the envelope checks, the `_meta` version lookup, and the
`resultType: "complete"` wrapper. Everything else reuses them.
</details>

<details>
<summary>Hint 2 · The approach</summary>

Split `handle` into two layers:

1. **Envelope and era:**
   - Reject a missing or wrong `jsonrpc`, or a missing `method`, with -32600.
   - Return `None` for notifications (no `id`).
   - Handle `initialize` by recording a legacy version.
   - Read `params._meta["io.modelcontextprotocol/protocolVersion"]`. If it's missing, that's legacy when an
     `initialize` has happened, and -32602 otherwise. If it's present but not a modern version, return -32022 with
     the supported and requested versions.
2. **`_dispatch(id, method, params, modern)`:** implement each method once, and add the modern-only fields
   (`resultType`, `ttlMs`) when `modern` is true.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- A tool that raises is a **result** with `isError: true` and the text `Error: <message>`, not a JSON-RPC error. The
  model can read a result and recover; a protocol error just looks like a broken server.
- An unknown tool name or non-object arguments, on the other hand, *is* a -32602 protocol error.
- A dict or list return value goes in `structuredContent` *and* as JSON text in `content`.
- `str(KeyError("x"))` includes the quotes. Use `exc.args[0]` for a `KeyError` if you want a clean message.
- `serve` must reply -32700 with `id: null` to a line that isn't JSON, skip blank lines, and flush after each reply.
- The demo server only starts under `if __name__ == "__main__":`, so importing the module for tests doesn't block on
  stdin.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_discover` | `ttlMs`, `instructions` or the `serverInfo` `_meta` key missing |
| `test_modern_list_and_call` | `resultType` not added in the modern era; numbers returned without `str()`; dict results without `structuredContent` |
| `test_tool_error_is_result` | Tool exception turned into a JSON-RPC error |
| `test_unsupported_version` | Error `data` missing the full supported list (modern then legacy) or the requested version |
| `test_missing_meta_without_handshake` | Requests without `_meta` served even though no `initialize` happened |
| `test_legacy_client_still_works` | Modern-only fields leak into legacy replies; an unknown legacy version not mapped to the newest legacy version |
| `test_invalid_requests` | `jsonrpc: "1.0"` or a missing method accepted |
| `test_unknown_method_and_tool` | Wrong error codes, or `ping` result missing `resultType` |
| `test_tool_registration_validation` | Tool name regex or schema type not checked at registration |
| `test_serve_stdio` | Parse errors not answered; replies written for notifications |
| `test_demo_server_subprocess` | Demo server not started under `__main__`; `lookup_policy` doesn't raise for bad ids |
