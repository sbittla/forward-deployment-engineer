# ex14 · Circuit breaker and bulkhead

**Module:** m02 · **Covers:** R28 Distributed systems, R22 Production hardening, R01 Python · **Time:** 45 min

## Learning objectives
- Contain failures of a flaky dependency with a circuit breaker.
- Limit concurrent access to a resource with a thread-safe bulkhead.
- Pair resilience patterns with a useful fallback for users.

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

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Circuit breaker and bulkhead".
Before I write code, teach me the circuit breaker state machine (closed, open, half-open), bulkheads, and how they
prevent cascading failures. Use short Python examples that are not the exercise solution. Then ask me three
questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m02-production-python/ex14-circuit-breaker/starter.py so that test_breaker.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`CircuitOpenError`, `BulkheadFull`, `CircuitBreaker`, `Bulkhead`. Constraints: Python 3.11+, the standard library
and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or
fde_kit. When you're done, run `pytest exercises/m02-production-python/ex14-circuit-breaker` and show me the output.
If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Circuit breaker and bulkhead" as a senior forward deployed engineer would before it ships to
a customer. Specifically: Is the half-open state limited to exactly one trial call under concurrency? Is the state
property consistent with call()? What fallback would you show the end user when the breaker is open? Rank findings
by customer impact, quote the line for each, and say which ones a test should catch.
```
