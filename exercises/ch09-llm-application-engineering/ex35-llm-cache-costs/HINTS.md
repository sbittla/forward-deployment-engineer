# ex35 hints · Response cache and cost accounting

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

The cache key is the whole design. Put every input that changes the answer into one dict (model, system, messages,
tools, and the extra keyword arguments), serialise it with `json.dumps(..., sort_keys=True)` and hash it with
SHA-256. Two requests that differ only in dict key order then produce the same key.

The cost model is arithmetic: tokens times price per million, divided by 1,000,000. Write the book's worked example
as a test first ($0.0276 and $0.0195 per request) and make the numbers come out.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- Store `key -> (stored_at, response)`. On a lookup, a hit needs `now - stored_at < ttl_s`; otherwise count a miss,
  call the model, and store the response if it's cacheable.
- **Cacheable** means `stop_reason == "end_turn"` and no tool calls.
- **Ledger:** keep `tenant -> {"requests", "cost_usd"}` (a `defaultdict` helps). Always count the request, and add the
  cost only when `cached` is False.
- **Cost model:** the only thing that changes with `cached_prefix` is the price of the system-prompt tokens:
  `price_in * cache_read` instead of `price_in`. The monthly figure multiplies by the requests that still reach the
  model, `requests * (1 - response_hit_rate)`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `sort_keys=True` sorts keys at every nesting level, which is what makes `{"content", "role"}` and
  `{"role", "content"}` hash the same.
- `max_tokens=10` and `max_tokens=20` must be different keys, so include the extra keyword arguments.
- Look up the price **before** recording anything, so an unknown model raises `KeyError` and leaves no half-recorded
  row. Never fall back to a price of 0.
- `over_budget` is strictly greater than: spending exactly the budget isn't over.
- Only the system prompt is the cached prefix. Documents and the question change per request, so they're always
  billed at the full input price, and the answer at the output price.
- Don't round `cost_per_request`. Round only the monthly total to 2 dp: a per-request cost of $0.000123 rounded to
  cents would make the whole month free.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_cache_hits_and_ttl` | System prompt left out of the key; TTL check uses `<=` the wrong way; hits not counted |
| `test_key_is_canonical` | Key built from `str(messages)` (order-sensitive), or extra kwargs ignored |
| `test_tool_calls_not_cached` | Every response cached regardless of stop reason |
| `test_empty_stats` | Division by zero when there have been no calls |
| `test_ledger` | Cached responses not counted as requests, or charged anyway; `>=` used for the budget |
| `test_unknown_model` | Unknown model priced at 0 instead of raising |
| `test_cost_per_request_worked_example` | Cache-read price applied to documents too, or applied when `cached_prefix` is False; no `ValueError` for negative tokens |
| `test_monthly_projection` | Hit rate not subtracted, total not rounded to 2 dp, or an out-of-range hit rate accepted |
| `test_cross_tenant_requests_do_not_share_entries` | System prompt left out of the cache key, so one tenant receives another's cached answer |
