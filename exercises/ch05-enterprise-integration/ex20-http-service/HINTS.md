# ex20 hints · Minimal HTTP service with auth and health

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Define the handler class *inside* `make_server`, so it can see `answer_fn` and `tokens` through the closure. Subclass
`BaseHTTPRequestHandler`, give it one `_send(status, payload)` helper that writes JSON, `Content-Length` and
`X-Request-ID`, and send every response through that helper.
</details>

<details>
<summary>Hint 2 · The approach</summary>

Have `do_GET` and `do_POST` both call one `_dispatch(method)` that works through a fixed order:

1. set the request id (echo the client's or generate one);
2. unknown path → 404;
3. wrong method → 405;
4. health → 200;
5. auth → 401;
6. size → 413;
7. parse and validate → 400;
8. call `answer_fn` → 200, or 500 if it raises.

A dict of `path -> allowed methods` makes steps 2 and 3 one lookup each.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Check `Content-Length` **before** reading the body. For the 413, read and discard up to 1 MiB in chunks, set
  `self.close_connection = True`, then respond. If you reply without draining, the client often sees a connection
  reset instead of your 413.
- `json.loads` can succeed and still return a list or a number. Check it's a dict before calling `.get`.
- In the 500 path, log the exception server-side, and send only `"internal error"` and the request id.
- Compare tokens with `hmac.compare_digest`. Override `log_message` if the default stderr access log is noisy in
  tests.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_health` | `X-Request-ID` header missing on health, or not a 32-character `uuid4().hex` |
| `test_answer_and_request_id_echo` | Client's `X-Request-ID` not echoed in the header and the body |
| `test_auth` | `Bearer ` prefix not checked, or auth applied after body parsing |
| `test_validation` | Non-dict JSON crashes the handler; empty or 2001-character question accepted |
| `test_too_large` | Body read before the size check, or the 413 sent without draining the request |
| `test_method_and_path` | 404 and 405 confused: a known path with the wrong method must be 405 |
| `test_internal_error_does_not_leak` | Exception text included in the 500 body |
