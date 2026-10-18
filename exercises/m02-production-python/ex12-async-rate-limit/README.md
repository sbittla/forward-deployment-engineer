# ex12 · Async fan-out with rate limiting

**Module:** m02 · **Covers:** R01 Python, R27 Performance, R28 Backend architecture · **Time:** 50 min

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

## Field notes
Measure the provider's actual limits (requests *and* tokens per minute) in the customer's tenant; they are often
lower than the docs because of org-level quotas.
