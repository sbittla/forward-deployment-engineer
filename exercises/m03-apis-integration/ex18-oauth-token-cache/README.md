# ex18 · OAuth2 client-credentials token cache

**Module:** m03 · **Covers:** R05 Integration, R17 Auth · **Time:** 45 min

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
