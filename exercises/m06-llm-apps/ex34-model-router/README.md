# ex34 · Cost/latency-aware model router with fallback

**Module:** m06 · **Covers:** R27 Cost & latency optimization, R08 LLM apps · **Time:** 50 min

## Scenario
The customer's volume is 2M requests/month. Sending everything to the most capable model blows the budget;
sending everything to the smallest model hurts quality on hard cases. Route each request to the cheapest model
that meets its quality and latency needs, and fail over when a model is overloaded.

> Prices below are exercise data. Always check the provider's current price list before quoting a customer.

## Your task
`MODELS` (provided) lists `name, tier (1-3), price_in, price_out ($ per 1M tokens), p50_ms`.

1. `estimate_cost(model, in_tokens, out_tokens) -> float` (USD).
2. `route(req) -> list[str]` — `req` has `min_tier`, `max_latency_ms`, `max_cost_usd`, `in_tokens`, `out_tokens`.
   Return all eligible models (tier ≥ `min_tier`, `p50_ms` ≤ `max_latency_ms`, estimated cost ≤ `max_cost_usd`)
   ordered cheapest first (ties: lower latency). Raise `NoRouteError` if none qualify.
3. `call_with_fallback(clients, order, messages, **kw) -> (response, attempts)` — try models in `order`;
   `clients[name]` has `.complete(messages, model=name, **kw)`. On an exception whose `status` is 429, 503 or 529
   (overloaded) move to the next model; any other exception propagates immediately. `attempts` is a list of
   `(model, "ok" | "<status>")`. If all fail, raise the last exception.
