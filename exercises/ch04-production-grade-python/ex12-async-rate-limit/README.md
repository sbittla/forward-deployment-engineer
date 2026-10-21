# ex12 · Async fan-out with rate limiting

**Chapter:** 4 · Production-Grade Python (`exercises/ch04-production-grade-python/`) · **Covers:** R01 Python, R27 Performance, R28 Backend architecture

## Learning objectives
- Bound concurrency and request rate for large LLM batch jobs.
- Implement a continuous-refill token bucket with a monotonic clock.
- Preserve input order and isolate per-item failures.

## Scenario
You need to classify 40,000 historical tickets with an LLM before Monday's readout. Sequential calls take 30
hours. Unbounded `asyncio.gather` gets you rate-limited in seconds. You need bounded concurrency **and** a
request-rate limit.

## Your task
1. `TokenBucket(rate, capacity)` — `await bucket.acquire()` waits until a token is available. Tokens refill
   continuously at `rate` per second up to `capacity`; the bucket starts full. Use `time.monotonic()`.
2. `gather_limited(factories, concurrency, bucket=None)` — `factories` is a list of zero-arg callables that return
   coroutines. Run at most `concurrency` at once, acquire a bucket token (if given) before starting each, and return
   results **in input order**. A raised exception is returned in its slot (do not cancel the others).
   Cancellation is not an item failure: `asyncio.CancelledError` propagates out of `gather_limited` and is never
   stored in a slot (catch `Exception`, not `BaseException`).

**Errors:** `TokenBucket` raises `ValueError` when `rate <= 0` or `capacity < 1`; `gather_limited` raises `ValueError` when `concurrency < 1` (a zero-size semaphore would wait forever).

### Fault-injection tests
The `test_fault_*` tests inject faults into a batch: two calls that hang forever, each bounded by `asyncio.timeout()`
inside its factory (the `TimeoutError` lands in its slot and the semaphore slot is released, so the batch still
finishes); a seeded 25% of calls failing under a `TokenBucket` (every other slot keeps its own result, in order);
and a batch canceled mid-flight (every started call sees the cancellation and runs its cleanup, and no new call
starts).

## Field notes
Measure the provider's actual limits (requests *and* tokens per minute) in the customer's tenant; they are often
lower than the docs because of org-level quotas.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch04-production-grade-python/ex12-async-rate-limit`.
- **Expected output:** all 9 tests fail against the starter; when you're done, all 9 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch04-production-grade-python/ex12-async-rate-limit`: all 9 pass.
- **Tests:** `test_async.py` (9 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The bucket is per-process, there is no per-call timeout (a hung call holds its semaphore
  slot), failed items aren't retried and every result is held in memory. Production wraps each call in
  `asyncio.timeout()`, feeds `429`/`Retry-After` back into the limiter, shares the limit across workers that share a
  quota, budgets tokens per minute as well as requests, and checkpoints results so a cancelled batch can resume.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Async fan-out with rate limiting".
Before I write code, teach me asyncio semaphores, token-bucket rate limiting, and why unbounded gather gets you
rate-limited. Use short Python examples that are not the exercise solution. Then ask me three questions to check my
understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch04-production-grade-python/ex12-async-rate-limit/starter.py so that test_async.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`TokenBucket`, `gather_limited`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only
(pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch04-production-grade-python/ex12-async-rate-limit` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Async fan-out with rate limiting" as a senior forward deployed engineer would before it ships
to a customer. Specifically: Can the token bucket go negative or busy-wait? Is a failing task's exception returned
in its slot without cancelling others? How would you add a tokens-per-minute limit as well as requests-per-second?
Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
