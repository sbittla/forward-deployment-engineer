# ex34 hints · Cost/latency-aware model router with fallback

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

`estimate_cost` is the same per-million-token arithmetic as ex03: `in_tokens * price_in / 1e6` plus the output side.
Check it against `test_cost` before you write `route`, which filters and sorts using it.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **route:** a list comprehension with the three conditions (tier, latency, cost), then sort with the key
  `(estimated cost, p50_ms)`. Raise `NoRouteError` when the list is empty.
- **call_with_fallback:** loop over `order`. Wrap each call in `try/except`. On failure, read
  `getattr(exc, "status", None)`. If it's in `FAILOVER_STATUS`, record `(name, str(status))`, remember the exception
  and continue; otherwise re-raise immediately. On success, record `(name, "ok")` and return.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Pass `model=name` through to `clients[name].complete(...)`, along with any extra keyword arguments (`max_tokens`).
- Statuses in `attempts` are strings (`"529"`), not ints.
- If every model fails over, raise the **last** exception, not a new one, so callers still see the status.
- A 400 means the request is wrong and every model would reject it. Don't fail over on it.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_cost` | Prices treated as per-thousand tokens |
| `test_route_cheapest_first` | Sorted by tier or name instead of estimated cost |
| `test_route_constraints` | `>` instead of `>=` on tier, or cost limit ignored |
| `test_fallback_on_overload` | 529 not in the fail-over set; status recorded as an int |
| `test_non_retryable_propagates` | Every error triggers fail-over, so the second client gets called |
| `test_all_fail` | Returns `None` instead of raising after the last model fails |
| `test_fails_over_on_timeout_and_5xx` | `TimeoutError` not caught; 500, 502 or 504 missing from the fail-over set |
| `test_malformed_reply_fails_over` | `accept` checked but the rejected reply returned anyway; no `MalformedReply` after the last model |
| `test_budget_refuses_before_the_call` | Budget checked after the call (the model already ran) or against the actual, not worst-case, cost |
| `test_budget_fails_closed` | A model over budget skipped instead of stopping, so a pricier fallback runs; unknown models priced at zero |
| `test_non_retryable_carries_attempts` | Attempts not attached to the propagated exception |
| `test_percentile` | Interpolated percentile instead of nearest rank; off-by-one in the rank |
| `test_route_comparison_is_reproducible` | Failed or malformed replies not charged; timed-out attempts counted at the model's latency |
