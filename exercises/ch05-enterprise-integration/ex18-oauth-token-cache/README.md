# ex18 · OAuth2 client-credentials token cache

**Chapter:** 5 · Enterprise Integration (`exercises/ch05-enterprise-integration/`) · **Covers:** R05 Integration, R17 Auth

## Learning objectives
- Cache OAuth2 client-credentials tokens with expiry skew.
- Make refresh single-flight under concurrency.
- Recover from a 401 with one invalidate-and-retry.

## Scenario
The customer's API gateway issues OAuth2 tokens (client-credentials grant) valid for 1 hour and rate-limits the
token endpoint to 10 requests/minute. Your 32-thread backfill job requested a new token on every call and got
locked out.

## Your task
`TokenProvider(token_url, client_id, client_secret, transport, clock=time.time, skew=60)` where
`transport(url, form: dict) -> dict` returns `{"access_token", "expires_in", "token_type"}` or raises.

1. `get_token()` — returns a cached token while `now < issued_at + expires_in - skew`; otherwise fetches a new one
   with form `{"grant_type": "client_credentials", "client_id": ..., "client_secret": ...}`.
   **Single-flight:** concurrent callers during a refresh must trigger exactly one transport call.
2. `invalidate()` — drop the cached token.
3. `call_with_auth(fn)` — calls `fn(token)`. If it raises an exception with `status == 401`, invalidate, fetch a
   fresh token and retry **once**. Other exceptions propagate.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "OAuth2 client-credentials token
cache". Before I write code, teach me the OAuth2 client-credentials grant, token caching with clock skew,
single-flight refresh, and safe 401 retry. Use short Python examples that are not the exercise solution. Then ask me
three questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch05-enterprise-integration/ex18-oauth-token-cache/starter.py so that test_oauth.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`TokenProvider`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is
allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch05-enterprise-integration/ex18-oauth-token-cache` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "OAuth2 client-credentials token cache" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Under 32 threads, can more than one refresh happen? Could a 401 loop forever? Is
the client secret ever logged or included in an exception? Rank findings by customer impact, quote the line for
each, and say which ones a test should catch.
```
