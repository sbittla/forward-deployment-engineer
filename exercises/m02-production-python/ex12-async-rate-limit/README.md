# ex12 · Async fan-out with rate limiting

**Module:** m02 · **Covers:** R01 Python, R27 Performance, R28 Backend architecture · **Time:** 50 min

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

**Errors:** `TokenBucket` raises `ValueError` when `rate <= 0` or `capacity < 1`; `gather_limited` raises `ValueError` when `concurrency < 1` (a zero-size semaphore would wait forever).

## Field notes
Measure the provider's actual limits (requests *and* tokens per minute) in the customer's tenant; they are often
lower than the docs because of org-level quotas.

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
Implement exercises/m02-production-python/ex12-async-rate-limit/starter.py so that test_async.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`TokenBucket`, `gather_limited`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only
(pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m02-production-python/ex12-async-rate-limit` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Async fan-out with rate limiting" as a senior forward deployed engineer would before it ships
to a customer. Specifically: Can the token bucket go negative or busy-wait? Is a failing task's exception returned
in its slot without cancelling others? How would you add a tokens-per-minute limit as well as requests-per-second?
Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
