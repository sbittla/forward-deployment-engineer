# ex14 hints · Circuit breaker and bulkhead

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Don't store the state as a string. Store two facts: the consecutive-failure count and the time the breaker opened
(`None` while closed). Then work out the state from them in the `state` property: no open time means `closed`; open
time plus `reset_timeout` reached means `half_open`; otherwise `open`. This is why reading `state` "evaluates the
timeout".
</details>

<details>
<summary>Hint 2 · The approach</summary>

In `call`, read the state once at the start:

- `open`: raise `CircuitOpenError` without calling `fn`.
- `closed` or `half_open`: call `fn`. On success, reset the counter and clear the open time. On failure, a
  `half_open` trial reopens the breaker straight away (record a new open time). A closed breaker increments the
  counter and opens once it reaches the threshold. Re-raise the original exception in both cases.

For the bulkhead, `threading.BoundedSemaphore(max_concurrent)` with `acquire(blocking=False)` does the counting for
you.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The timer restarts on a failed trial: set the open time to *now*, not the original time. The test checks the
  breaker is still open at 24 and half-open at 25 after a failure at 15.
- The boundary is `>=`: at exactly `reset_timeout` seconds the breaker is half-open.
- Exactly one trial in half-open: a flag set under a lock stops a second concurrent caller getting through.
- `__exit__` must release the semaphore even if the body raised, and return `False` so the exception propagates.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_opens_after_threshold` | `fn` still called while open, or the threshold is off by one |
| `test_success_resets_counter` | Counting total failures rather than consecutive ones |
| `test_half_open_success_closes` | `state` computed with `>` instead of `>=`, or success doesn't clear the open time |
| `test_half_open_failure_reopens_and_restarts_timer` | Failed trial keeps the original open time, or only increments the counter |
| `test_bulkhead` | Slot not released on exit, or entering blocks instead of raising `BulkheadFull` |
| `test_bulkhead_threads` | A plain integer counter without a lock, so threads race past the limit |
| `test_fault_outage_load_on_dependency_is_bounded` | A failed half-open trial doesn't restart the timer, so the dependency is called every second |
| `test_fault_half_open_admits_one_trial_under_concurrency` | No "trial in flight" flag, so every caller in the half-open window reaches the dependency |
