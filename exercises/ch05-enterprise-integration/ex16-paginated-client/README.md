# ex16 · Paginated REST client with rate-limit headers

**Chapter:** 5 · Enterprise Integration (`exercises/ch05-enterprise-integration/`) · **Covers:** R05 APIs & system integration

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

`test_invalid_or_expired_token_is_not_retried` pins the negative case: a `401` or `403` (an invalid or expired
token) raises `ApiError` after one request, with no sleep and no retry.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch05-enterprise-integration/ex16-paginated-client`.
- **Expected output:** all 8 tests fail against the starter; when you're done, all 8 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch05-enterprise-integration/ex16-paginated-client`:
  all 8 pass.
- **Tests:** `test_client.py` (8 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The transport is injected and the API token is a plain string. A production client sets
  connect and read timeouts, parses `Retry-After` as either seconds or an HTTP date, adds random jitter when several
  workers share one key, and reads the token from the customer's secret manager.

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
Implement exercises/ch05-enterprise-integration/ex16-paginated-client/starter.py so that test_client.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Response`,
`ApiError`, `ApiClient`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml
is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch05-enterprise-integration/ex16-paginated-client` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Paginated REST client with rate-limit headers" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Does the client sleep before the next request (not after the last)? Are
header lookups case-insensitive everywhere? What happens if the API returns the same cursor twice? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
