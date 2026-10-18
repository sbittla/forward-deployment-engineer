# ex34 · Cost/latency-aware model router with fallback

**Module:** m06 · **Covers:** R27 Cost & latency optimization, R08 LLM apps · **Time:** 50 min

## Learning objectives
- Route each request to the cheapest model that meets quality and latency needs.
- Fail over on overload errors only, and record every attempt.
- Explain routing decisions with cost estimates.

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

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Cost/latency-aware model router with
fallback". Before I write code, teach me model routing, cost estimation per request, latency budgets, and fallback
on 429/503/529 overload errors. Use short Python examples that are not the exercise solution. Then ask me three
questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m06-llm-apps/ex34-model-router/starter.py so that test_router.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Model`,
`NoRouteError`, `estimate_cost`, `route`, `call_with_fallback`. Constraints: Python 3.11+, the standard library and
the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit.
When you're done, run `pytest exercises/m06-llm-apps/ex34-model-router` and show me the output. If the README and
the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Cost/latency-aware model router with fallback" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Could a non-retryable error (400, auth) trigger fallback and hide a
bug? Are ties broken deterministically? Where would quality evals plug into the min_tier decision? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
