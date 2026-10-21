# ex30 hints · Demo chat UI served from Python

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Keep the HTML page as one module-level string with a placeholder where the demo banner goes, and fill it once in
`make_app` depending on `demo_mode`. Write the page by hand in a browser first if that helps. Then wrap it in a
`BaseHTTPRequestHandler` subclass defined inside `make_app`, so it can see `llm`.

Write `sse` and `relay` before the streaming endpoint. They only need an iterator and something with `write` and
`flush`, so an `io.BytesIO` is enough to try them out.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- `do_GET`: `/` returns the page with `text/html; charset=utf-8`; anything else returns 404 JSON.
- `do_POST`: only `/api/chat` and `/api/chat/stream` are allowed. Read `Content-Length` bytes, parse the JSON,
  validate `q` (a non-empty string) and `history` (a list of `{role, content}` dicts, defaulting to `[]`), then call
  `llm.complete` with `system=SYSTEM_PROMPT`. Time the call with `time.perf_counter()` and return whole milliseconds.
- In the page's script, create a `div` per message and set its `textContent`.
- `relay`: a `try` around the loop over `chunks`, with one `except` for `BrokenPipeError`/`ConnectionResetError`
  (return `"cancelled"`), one for any other exception (write the error event, return `"error"`), and a `finally`
  that closes `chunks`.
- `/api/chat/stream`: validate exactly as `/api/chat` does, send the three headers without a `Content-Length`, then
  pass `relay` a generator that calls `llm.complete` and yields the answer word by word (for example
  `re.findall(r"\S+\s*|\s+", text)`).
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The test fails if the string `innerHTML` appears **anywhere** in the page, including comments. Don't mention it at
  all.
- The messages sent to the model are `history + [{"role": "user", "content": q}]`, in that order.
- Return `response.model` from the LLM response. Don't hard-code a model name.
- Check the parsed body is a dict before calling `.get`, and reject a `history` that isn't a list.
- `SYSTEM_PROMPT` must tell the model to say when it doesn't **know** (the test looks for that word).
- The disconnect test counts how many pieces `relay` pulls. Stop at the first failed write; don't drain the rest of
  the upstream "to be tidy". Closing it is what stops the model from generating for a user who has left.
- Never put `str(exc)` in the error event. The test's upstream error message contains a fake key.
- Without a `Content-Length`, the client reads until the connection closes, so set `self.close_connection = True`
  after the stream.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_page` | Missing an exact attribute (`<form id="chat-form"`, `name="q"`, `id="log"`); the word `innerHTML` present |
| `test_no_banner_when_live` | Banner always rendered, or its id left in the page when `demo_mode` is False |
| `test_chat_api` | History and question sent in the wrong order; system prompt not passed; latency not an `int` |
| `test_chat_validation` | Non-JSON body or a non-list history raises a 500 instead of returning 400 |
| `test_404` | Unknown GET paths return the page instead of 404 |
| `test_sse_format` | Missing the blank line (`\n\n`) that ends an event, or `data` not JSON-encoded |
| `test_relay_deltas_and_keepalive` | `None` written as a delta instead of a `: keep-alive` comment; no `done` event at the end |
| `test_relay_cancels_upstream_on_disconnect` | Upstream iterator not closed; reading continued after the failed write; exception not caught |
| `test_relay_upstream_error` | Exception text sent to the browser, or a `done` event written after the error |
| `test_stream_endpoint` | Missing SSE headers; the whole answer sent as one delta; validation skipped on the stream path |
