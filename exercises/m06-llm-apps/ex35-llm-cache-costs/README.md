# ex35 · Response cache and cost accounting

**Module:** m06 · **Covers:** R27 Cost optimization, R08 LLM apps · **Time:** 50 min

## Scenario
Finance wants per-tenant LLM spend for chargeback, and your analytics show 30% of copilot questions are exact
repeats ("How do I reset my password?"). Add an exact-match response cache and a ledger that prices usage.

## Your task
1. `CachedLLM(llm, ttl_s, clock=time.time)` exposing `complete(messages, system=None, tools=None, model=None, **kw)`:
   - cache key = SHA-256 of canonical JSON (`sort_keys=True`) of `{model, system, messages, tools}` + extra kwargs
   - return a cached response if younger than `ttl_s`; only cache responses with `stop_reason == "end_turn"`
     (never cache tool calls); expired entries are refetched
   - `stats()` → `{"hits", "misses", "hit_rate"}` (hit_rate rounded to 3 dp, 0.0 when no calls)
2. `CostLedger(prices)` where `prices[model] = (usd_per_mtok_in, usd_per_mtok_out)`:
   - `record(tenant, response, cached=False)` — cached responses cost 0 but still count as requests
   - `by_tenant() -> {tenant: {"requests", "cost_usd"}}` (cost rounded to 6 dp)
   - `over_budget(budgets: {tenant: usd}) -> list[str]` tenants whose spend is **strictly** greater, sorted
   - unknown model → `KeyError` (never silently price at 0)

## Field notes
Provider-side prompt caching (caching a long shared prefix such as a system prompt or document) is a different,
complementary lever: it cuts input-token cost on every call, not just exact repeats.
