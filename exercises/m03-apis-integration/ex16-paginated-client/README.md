# ex16 · Paginated REST client with rate-limit headers

**Module:** m03 APIs & Integration · **Covers:** R05 APIs & system integration · **Time:** 45 min

## Scenario
You need every ticket from the customer's helpdesk API (cursor pagination, 100 per page, strict rate limits) to
build the RAG corpus. The vendor's docs say: respect `Retry-After` on 429 and stop when
`X-RateLimit-Remaining: 0` until `X-RateLimit-Reset` (epoch seconds).

## Your task
`ApiClient(base_url, token, transport, sleep=time.sleep, clock=time.time, max_retries=3)` where
`transport(method, url, headers, params) -> Response(status, headers, body)` (`body` is parsed JSON).

1. `get(path, params=None)`:
   - sends `Authorization: Bearer <token>` and `Accept: application/json`
   - on 429: sleep `Retry-After` seconds (default 1) and retry, up to `max_retries` retries, then raise `ApiError`
   - other status ≥ 400: raise `ApiError(status, body)` immediately
   - after any response with `X-RateLimit-Remaining == "0"`, sleep until `X-RateLimit-Reset` (if in the future)
     **before the next request**
2. `list_all(path, params=None, max_pages=1000)` — follows `body["next_cursor"]` (pass it back as `cursor`
   param) and yields every item in `body["data"]`. Raise `ApiError` if `max_pages` is exceeded (cursor loop guard).

Header lookups are case-insensitive.
