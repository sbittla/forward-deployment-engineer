# ex14 · Circuit breaker and bulkhead

**Module:** m02 · **Covers:** R28 Distributed systems, R22 Production hardening, R01 Python · **Time:** 45 min

## Scenario
The customer's legacy policy-lookup service falls over every afternoon. When it does, your copilot's threads
pile up waiting on 30-second timeouts and the whole app goes down with it. Contain the blast radius.

## Your task
1. `CircuitBreaker(failure_threshold=5, reset_timeout=30.0, clock=time.monotonic)`
   - `call(fn, *args, **kwargs)`:
     - **closed**: run `fn`. Each failure increments a consecutive-failure counter; a success resets it. When the
       counter reaches `failure_threshold`, the breaker **opens** (record the time).
     - **open**: raise `CircuitOpenError` without calling `fn` until `reset_timeout` has elapsed, then move to
       **half_open**.
     - **half_open**: allow exactly one trial call. Success → closed (counter reset). Failure → open again
       (timer restarts).
   - `state` property returns `"closed" | "open" | "half_open"` (evaluate the timeout when read).
2. `Bulkhead(max_concurrent)` — a context manager guarding a resource. Entering when `max_concurrent` holders are
   already inside raises `BulkheadFull` immediately (no waiting). Must be thread-safe.

## Field notes
Pair breakers with a useful fallback: "Policy lookup is temporarily unavailable — here is the cached clause from
yesterday" beats a spinner.
