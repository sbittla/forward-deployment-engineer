# ex16 hints · Paginated REST client with rate-limit headers

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write a tiny case-insensitive header lookup first (lowercase both names and compare). Then write `get` without any
rate-limit handling: build the URL, send the two headers, raise `ApiError` on 400 and above. `list_all` is a loop
around `get`, so leave it until `get` works.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- Join the URL so there's exactly one slash between the base and the path, whatever the caller passes
  (`.../api/` + `/tickets`).
- `get` loops for `max_retries + 1` attempts. On a 429, sleep `Retry-After` (default 1) and go round again, unless
  this was the last attempt, in which case raise.
- `list_all` is a **generator**: copy the params, call `get`, `yield from` the data, then set `params["cursor"]` to
  the next cursor, or return when there isn't one.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The proactive wait applies *before the next request*, not straight after the response. Store a "wait until"
  timestamp when you see `X-RateLimit-Remaining: 0`. At the top of each request, sleep `wait_until - clock()` if
  that's positive, then clear the timestamp.
- Header values are strings: convert `Retry-After` and `X-RateLimit-Reset` with `float(...)`.
- Don't put the cursor into the caller's params dict. Copy it, or the first request of the next call starts
  mid-stream.
- For the cursor loop guard, stop after `max_pages` iterations and raise `ApiError`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_auth_headers_and_pagination` | Double or missing slash in the URL; cursor sent on the first request; caller's params changed |
| `test_retry_after` | Retry-After read case-sensitively, or the default of 1 second missing |
| `test_429_exhausted` | One request too few or too many: `max_retries=3` means 4 requests in total |
| `test_client_error` | `ApiError` doesn't keep `status` and `body` as attributes |
| `test_proactive_rate_limit_wait` | Sleeping right after the response (and after the last page), or not using the injected clock |
| `test_cursor_loop_guard` | No page limit, so a repeating cursor loops forever |
