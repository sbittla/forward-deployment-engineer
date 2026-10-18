# ex10 · Retries, backoff, jitter, idempotency

**Module:** m02 · **Covers:** R01 Python, R22 Production hardening, R15 Reliability · **Time:** 50 min

## Learning objectives
- Retry only transient failures with capped exponential backoff and full jitter.
- Honour Retry-After from the server.
- Make side-effecting calls safe to retry with idempotency keys.

## Scenario
The customer's ERP API returns `429` and `503` under load. Your naive integration hammered it in a tight loop and
got the FDE team's IP blocked. Worse, a retried `POST /refunds` paid a customer twice.

## Your task
1. `retry(max_attempts=4, base_delay=0.5, max_delay=8.0, sleep=time.sleep, rng=random.random)` — a decorator.
   - Retry when the exception is a `ConnectionError`/`TimeoutError`, or has a `status` attribute in
     `{408, 429, 500, 502, 503, 504}`. Anything else is re-raised immediately.
   - Delay before retry *n* (0-based) uses **full jitter**: `rng() * min(max_delay, base_delay * 2**n)`.
   - If the exception has a numeric `retry_after` attribute, sleep exactly that instead.
   - After `max_attempts` total attempts, re-raise the last exception.
2. `IdempotencyStore.run(key, payload, fn)`:
   - First call with a key runs `fn(payload)` and stores the result.
   - Later calls with the same key **and same payload** return the stored result without calling `fn`.
   - Same key with a different payload raises `IdempotencyConflict`.
   - If `fn` raises, nothing is stored (a retry may run it again).

Payload equality: compare a SHA-256 of `json.dumps(payload, sort_keys=True)`.

## Field notes
Retries without idempotency turn a reliability fix into a money bug. Always ask the customer's API team which
endpoints accept an `Idempotency-Key` header.

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
Implement exercises/m02-production-python/ex10-retry-backoff/starter.py so that test_retry.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `retry`,
`IdempotencyConflict`, `IdempotencyStore`. Constraints: Python 3.11+, the standard library and the repo's fde_kit
package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done,
run `pytest exercises/m02-production-python/ex10-retry-backoff` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Retries, backoff, jitter, idempotency" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Could the decorator retry a 400 or a programming error? Is the delay sequence
correct for attempt 0? Can two concurrent callers with the same idempotency key both run fn? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
