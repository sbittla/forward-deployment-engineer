# ex16 · Paginated REST client with rate-limit headers

**Module:** m03 APIs & Integration · **Covers:** R05 APIs & system integration · **Time:** 45 min

## Learning objectives
- Consume a paginated REST API completely and safely.
- Respect Retry-After and rate-limit headers before the next request.
- Guard against infinite cursor loops.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Paginated REST client with
rate-limit headers". Before I write code, teach me cursor pagination, HTTP 429 handling, X-RateLimit headers, and
case-insensitive header handling. Use short Python examples that are not the exercise solution. Then ask me three
questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m03-apis-integration/ex16-paginated-client/starter.py so that test_client.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Response`,
`ApiError`, `ApiClient`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml
is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m03-apis-integration/ex16-paginated-client` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Paginated REST client with rate-limit headers" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Does the client sleep before the next request (not after the last)? Are
header lookups case-insensitive everywhere? What happens if the API returns the same cursor twice? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
