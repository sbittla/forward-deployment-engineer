# ex35 · Response cache and cost accounting

**Module:** m06 · **Covers:** R27 Cost optimization, R08 LLM apps · **Time:** 50 min

## Learning objectives
- Cache exact-repeat LLM responses safely with a TTL.
- Never cache tool calls or incomplete responses.
- Attribute LLM spend per tenant for chargeback.

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

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Response cache and cost accounting".
Before I write code, teach me response caching vs provider-side prompt caching, cache keys over canonical JSON, and
per-tenant cost accounting. Use short Python examples that are not the exercise solution. Then ask me three
questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m06-llm-apps/ex35-llm-cache-costs/starter.py so that test_cache_costs.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `CachedLLM`,
`CostLedger`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed
where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m06-llm-apps/ex35-llm-cache-costs` and show me the output. If the README and the tests disagree, stop and
tell me instead of guessing.
```
**Review**
```text
Review my solution to "Response cache and cost accounting" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Does the cache key include every parameter that changes the output? Could one
tenant receive another tenant's cached answer? Is an unknown model ever priced at zero? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
