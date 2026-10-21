# ex12 hints · Async fan-out with rate limiting

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write `gather_limited` without the bucket first. An `asyncio.Semaphore(concurrency)` bounds how many jobs run at once,
and a results list pre-sized to `len(factories)` keeps input order however the jobs finish. Add the bucket once that
passes.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- Wrap each factory in an inner coroutine `run(i, factory)` that takes the semaphore, awaits `factory()` and writes
  the result to slot `i`. Catch exceptions there and store the exception object in the slot.
- `asyncio.gather` all the `run` coroutines.
- **Token bucket:** store the current token count (as a float) and the last refill time. On `acquire`, add
  `elapsed * rate` tokens (capped at capacity). If you have at least one token, take it. If not, sleep for the time
  until the next token and check again.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Call `factory()` *inside* the semaphore, after taking the bucket token. That's why the inputs are factories: no
  job (and none of the work its constructor might do) exists until it has a slot.
- Check `concurrency < 1` before creating the semaphore. A zero-size semaphore makes every job wait forever.
- Concurrent waiters on the bucket can all see "no tokens" and wake at the same moment. Holding an `asyncio.Lock`
  inside `acquire` hands tokens out one at a time.
- The bucket starts full: set the token count to `capacity` in `__init__`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_order_and_concurrency_bound` | Results appended as they finish (order lost); peak is not 4 because the semaphore wraps the wrong code |
| `test_exceptions_in_slot` | Exception propagates out of `gather` instead of being stored in its slot |
| `test_bucket_limits_rate` | Refill not continuous (whole seconds only), or bucket acquired outside the job flow |
| `test_bucket_starts_full` | Initial token count of 0 |
| `test_invalid_limits` | Validation missing in `TokenBucket.__init__`, or `concurrency=0` hangs instead of raising |
