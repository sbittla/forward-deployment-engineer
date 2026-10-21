# ex10 · Retries, backoff, jitter, idempotency

**Chapter:** 4 · Production-Grade Python (`exercises/ch04-production-grade-python/`) · **Covers:** R01 Python, R22 Production hardening, R15 Reliability

## Learning objectives
- Retry only transient failures with capped exponential backoff and full jitter.
- Honour Retry-After from the server.
- Make side-effecting calls safe to retry with idempotency keys.

## Scenario
The customer's ERP API returns `429` and `503` under load. Your naive integration hammered it in a tight loop and
got the FDE team's IP blocked. Worse, a retried `POST /refunds` paid a customer twice.

## Your task
1. `retry(max_attempts=4, base_delay=0.5, max_delay=8.0, sleep=time.sleep, rng=random.random, deadline=None,
   clock=time.monotonic, on_retry=None)` — a decorator.
   - Retry when the exception is a `ConnectionError`/`TimeoutError`, or has a `status` attribute in
     `{408, 429, 500, 502, 503, 504}`. Anything else is re-raised immediately.
   - Delay before retry *n* (0-based) uses **full jitter**: `rng() * min(max_delay, base_delay * 2**n)`.
   - If the exception has a numeric `retry_after` attribute, sleep exactly that instead.
   - After `max_attempts` total attempts, re-raise the last exception.
   - `deadline` (seconds, optional) is a time budget measured with `clock` from just before the first attempt. Before
     each sleep, if `clock() + delay >= start + deadline`, re-raise the current exception without sleeping. This
     also caps `retry_after`. With `deadline=None` there is no budget.
   - `on_retry` (optional) is called as `on_retry(attempt, delay, exc)` just before each sleep: one event per retry,
     none for the final failure or a non-retryable error. Use it to log each retry as a structured event.
2. `IdempotencyStore.run(key, payload, fn)`:
   - First call with a key runs `fn(payload)` and stores the result.
   - Later calls with the same key **and same payload** return the stored result without calling `fn`.
   - Same key with a different payload raises `IdempotencyConflict`.
   - If `fn` raises, nothing is stored (a retry may run it again).

Payload equality: compare a SHA-256 of `json.dumps(payload, sort_keys=True)`.

### Fault-injection tests
The `test_fault_*` tests drive the decorator with fake dependencies: one that fails a seeded 30% of calls (retries
stay bounded per client), a full outage across 100 clients (exactly `clients × max_attempts` calls, with jittered
waits), a dependency that hangs 3 seconds per call against a 10-second `deadline`, a `Retry-After` longer than the
deadline (no sleep), and a server that applies a refund but loses the response twice (paid once, because the retry
reuses the idempotency key against the server's `IdempotencyStore`).

## Field notes
Retries without idempotency turn a reliability fix into a money bug. Always ask the customer's API team which
endpoints accept an `Idempotency-Key` header.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch04-production-grade-python/ex10-retry-backoff`.
- **Expected output:** all 15 tests fail against the starter; when you're done, all 15 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch04-production-grade-python/ex10-retry-backoff`:
  all 15 pass.
- **Tests:** `test_retry.py` (15 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Without `deadline` the decorator has no time budget (a `Retry-After` of an hour is slept in
  full, as `test_boundary_retry_after_is_not_capped_by_a_deadline` pins), it retries whatever it wraps, and the
  idempotency store is in-memory with no reservation. Production always sets a deadline, retries only idempotent or
  keyed calls, logs each retry through `on_retry` with the correlation id, and uses a durable shared store that
  reserves the key under a unique constraint before the side effect runs.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Retries, backoff, jitter,
idempotency". Before I write code, teach me transient vs permanent errors, exponential backoff with full jitter,
Retry-After, and why retries without idempotency create duplicate payments. Use short Python examples that are not
the exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to
re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch04-production-grade-python/ex10-retry-backoff/starter.py so that test_retry.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `retry`,
`IdempotencyConflict`, `IdempotencyStore`. Constraints: Python 3.11+, the standard library and the repo's fde_kit
package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done,
run `pytest exercises/ch04-production-grade-python/ex10-retry-backoff` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Retries, backoff, jitter, idempotency" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Could the decorator retry a 400 or a programming error? Is the delay sequence
correct for attempt 0? Can two concurrent callers with the same idempotency key both run fn? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
