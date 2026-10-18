# ex10 · Retries, backoff, jitter, idempotency

**Module:** m02 · **Covers:** R01 Python, R22 Production hardening, R15 Reliability · **Time:** 50 min

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
