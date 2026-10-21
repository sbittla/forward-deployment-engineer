# ex10 hints · Retries, backoff, jitter, idempotency

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

`retry(...)` takes arguments, so it's a decorator *factory*: a function that returns a decorator, which returns the
wrapper. Use `functools.wraps`. Write a separate `_retryable(exc)` predicate first and test it by itself: it should
return True for `ConnectionError`, `TimeoutError` and the listed status codes.
</details>

<details>
<summary>Hint 2 · The approach</summary>

Inside the wrapper, loop `for attempt in range(max_attempts)`. Return on success. On an exception, re-raise
immediately if it isn't retryable *or* this was the last attempt. Otherwise work out the delay and call the injected
`sleep(delay)` before looping again.

For the store, keep `key -> (payload_hash, result)`. Look the key up first; only call `fn` when the key is new.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The first delay uses `n = 0`, so with `rng() = 1.0` the sequence is `0.5, 1.0, 2.0`. Using the attempt number
  starting from 1 doubles every delay.
- `retry_after` replaces the computed delay entirely. Use `getattr(exc, "retry_after", None)` and check it's a
  number.
- Hash the payload with `json.dumps(..., sort_keys=True)` so `{"amount": 10, "order": "A"}` and
  `{"order": "A", "amount": 10}` are the same payload.
- Store the result only *after* `fn` returns. If `fn` raises, nothing is recorded, so a retry can run it again.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_retries_then_succeeds_with_exponential_backoff` | Exponent starts at 1, or `rng()` not applied |
| `test_caps_at_max_delay` | `min(max_delay, ...)` applied after multiplying by `rng()` instead of before |
| `test_retry_after_wins` | `retry_after` ignored, or added to the computed delay |
| `test_non_retryable_raises_immediately` | Everything retried; a 400 must be raised on the first attempt |
| `test_gives_up` | Sleeping after the final attempt, or one attempt too many |
| `test_jitter_uses_rng` | Using `random.random` directly instead of the injected `rng` |
| `test_idempotency` | Payload hashed without `sort_keys`, or the conflict check skipped |
| `test_failed_call_not_cached` | Result (or the key) stored before `fn` has succeeded |
| `test_boundary_retry_after_is_not_capped_by_a_deadline` | `retry_after` clamped to `max_delay`; the spec says sleep exactly that (the missing deadline is a documented limitation) |
