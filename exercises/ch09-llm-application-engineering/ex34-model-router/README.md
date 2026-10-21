# ex34 · Cost/latency-aware model router with fallback

**Chapter:** 9 · LLM Application Engineering (`exercises/ch09-llm-application-engineering/`) · **Covers:** R27 Cost & latency optimization, R08 LLM apps

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
   `clients[name]` has `.complete(messages, model=name, **kw)`. On an exception whose `status` is in
   `FAILOVER_STATUS` (provided: 429, 500, 502, 503, 504, 529, overloaded or transient server errors) move to the next
   model; any other exception propagates immediately. `attempts` is a list of `(model, "ok" | "<status>")`. If all
   fail, raise the last exception. Every exception `call_with_fallback` raises carries the list as `.attempts`.

### Provider failures, budgets and a reproducible comparison
`call_with_fallback(clients, order, messages, *, accept=None, budget=None, in_tokens=0, **kw)` adds three
keyword-only options; with none of them it behaves exactly as above.

4. **Timeouts.** A built-in `TimeoutError` fails over like an overload and is recorded as `(model, "timeout")`.
5. **Malformed replies.** `accept(response) -> bool` checks a reply (for example, that it parses as the expected
   JSON). A rejected reply is recorded as `(model, "malformed")` and the next model is tried; if the last one is
   rejected, raise `MalformedReply` (provided).
6. **A hard budget.** `Budget(limit_usd, spent_usd=0.0)` (a dataclass; implement its methods): `remaining()` is
   `limit_usd - spent_usd`; `check(cost_usd)` raises `BudgetExceeded` (provided) when `spent_usd + cost_usd` would
   exceed `limit_usd`; `charge(cost_usd)` adds to `spent_usd`. With a budget, **before** each call compute the
   worst case, `estimate_cost(model, in_tokens, kw.get("max_tokens", 1024))`, and `check` it. If it doesn't fit,
   record `(model, "budget")` and raise `BudgetExceeded` without calling that model or any later one (fail
   closed: a failover to a pricier model is refused too). A model not in `MODELS` can't be priced, so raise
   `BudgetExceeded` before calling it. After every reply that comes back, accepted or not, `charge` its actual cost
   from `response.input_tokens` and `response.output_tokens`: a malformed reply is still billed.
7. `percentile(values, q) -> value`: nearest rank, the value at position `ceil(q / 100 * n)` (1-based) of the
   sorted values. `ValueError` for an empty list.
8. `simulate(tasks, order, clients, latency_ms, *, accept=None, timeout_ms=5000, in_tokens=0, **kw) -> dict` replays
   a fixed task set (each task is a `messages` list) through one route on a simulated clock. Use one unlimited
   `Budget(math.inf)` to total the cost, and call `call_with_fallback` per task; a task succeeds if it returns.
   A task's latency is the sum over its attempts of `latency_ms[model]`, or `timeout_ms` for a `"timeout"` attempt.
   Return `{"tasks", "successes", "success_rate", "p50_ms", "p95_ms", "cost_usd", "cost_per_request",
   "cost_per_success"}`: rate rounded to 4 places, costs to 6, `cost_per_success` is `None` when nothing succeeded.
   The test compares three routes on 20 scripted tasks (a timeout, a 429, a 503, malformed JSON on four hard tasks
   and one provider-wide outage); the same inputs must give the same numbers every run.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch09-llm-application-engineering/ex34-model-router`.
- **Expected output:** all 17 tests fail against the starter; when you're done, all 17 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch09-llm-application-engineering/ex34-model-router`: all 17 pass.
- **Tests:** `test_router.py` (17 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Prices, tiers and latencies are static exercise data, failover keys on a status attribute
  of a fake exception, and `simulate` uses a fixed latency per model, so its p95 shows the cost of failover, not real
  tail latency. Production routing reads a dated price table and measured latencies, maps the real SDK's error
  classes, adds backoff and a circuit breaker, and alerts on sustained failover.

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
Implement exercises/ch09-llm-application-engineering/ex34-model-router/starter.py so that test_router.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Model`,
`NoRouteError`, `estimate_cost`, `route`, `call_with_fallback`. Constraints: Python 3.11+, the standard library and
the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit.
When you're done, run `pytest exercises/ch09-llm-application-engineering/ex34-model-router` and show me the output. If the README and
the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Cost/latency-aware model router with fallback" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Could a non-retryable error (400, auth) trigger fallback and hide a
bug? Are ties broken deterministically? Where would quality evals plug into the min_tier decision? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
