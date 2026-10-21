# ex18 hints · OAuth2 client-credentials token cache

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Store two things: the current token and the time it stops being usable, `issued_at + expires_in - skew`. A small
`_valid()` helper (token present and `clock() < expires_at`) keeps `get_token` readable. Get the single-threaded
caching test passing before you think about threads.
</details>

<details>
<summary>Hint 2 · The approach</summary>

Single-flight is **double-checked locking**:

- if the token is valid, return it without taking a lock;
- otherwise take a `threading.Lock` and check *again* inside it;
- only fetch if it's still invalid.

The fifteen threads that queued behind the first one find a fresh token when they get the lock, and return it
without calling the transport.

`call_with_auth` is a `try/except` around one call, followed by a single retry outside the `except` block.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Record `issued_at` *before* calling the transport. A slow token endpoint shouldn't extend the token's life.
- The expiry boundary is strict: with `expires_in=3600` and `skew=60`, the token is reused at 3539 seconds and
  refreshed at 3540.
- Check `getattr(exc, "status", None) == 401` and re-raise anything else unchanged.
- The retry happens **once**. If the second call also gets a 401, let it propagate; don't loop.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_caches_until_skew` | Skew not subtracted, or `<=` used at the boundary; form fields misnamed |
| `test_single_flight` | No lock, or the validity check isn't repeated inside the lock |
| `test_retry_once_on_401` | Token not invalidated before the retry, so the same `tok1` is sent again |
| `test_401_twice_propagates_and_other_errors` | Retry loops on repeated 401s, or non-401 errors are swallowed |
| `test_invalidate` | `invalidate` clears the token but leaves the expiry, or vice versa |
