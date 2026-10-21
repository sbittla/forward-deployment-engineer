# ex14 · Circuit breaker and bulkhead

**Chapter:** 4 · Production-Grade Python (`exercises/ch04-production-grade-python/`) · **Covers:** R28 Distributed systems, R22 Production hardening, R01 Python

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch04-production-grade-python/ex14-circuit-breaker`.
- **Expected output:** all 6 tests fail against the starter; when you're done, all 6 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch04-production-grade-python/ex14-circuit-breaker`:
  all 6 pass.
- **Tests:** `test_breaker.py` (6 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The breaker counts consecutive failures in one process and the bulkhead guards threads in
  that process only. Production needs a timeout on every protected call (a breaker never sees a call that hangs), a
  fallback a user accepts, breaker state and rejections exported as metrics, and thresholds tuned from measured error
  rates.

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
Implement exercises/ch04-production-grade-python/ex14-circuit-breaker/starter.py so that test_breaker.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`CircuitOpenError`, `BulkheadFull`, `CircuitBreaker`, `Bulkhead`. Constraints: Python 3.11+, the standard library
and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or
fde_kit. When you're done, run `pytest exercises/ch04-production-grade-python/ex14-circuit-breaker` and show me the output.
If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Circuit breaker and bulkhead" as a senior forward deployed engineer would before it ships to
a customer. Specifically: Is the half-open state limited to exactly one trial call under concurrency? Is the state
property consistent with call()? What fallback would you show the end user when the breaker is open? Rank findings
by customer impact, quote the line for each, and say which ones a test should catch.
```
