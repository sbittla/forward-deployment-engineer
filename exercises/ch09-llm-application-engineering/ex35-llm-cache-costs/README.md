# ex35 · Response cache and cost accounting

**Chapter:** 9 · LLM Application Engineering (`exercises/ch09-llm-application-engineering/`) · **Covers:** R27 Cost optimization, R08 LLM apps

## Learning objectives
- Cache exact-repeat LLM responses safely with a TTL.
- Never cache tool calls or incomplete responses.
- Attribute LLM spend per tenant for chargeback.
- Project monthly model cost from token counts, with prompt-cache read pricing.

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
3. `cost_per_request(system, docs, question, output, price_in=3.0, price_out=15.0, cached_prefix=False,
   cache_read=0.1) -> float`: dollars for one request from its token counts (system prompt, retrieved documents,
   question, answer). Prices are USD per million tokens. With `cached_prefix=True` the system-prompt tokens are a
   prompt-cache read billed at `price_in * cache_read`; documents and question are always billed at `price_in`, the
   answer at `price_out`. Any negative token count → `ValueError`.
4. `monthly_cost(per_request, requests, response_hit_rate=0.0) -> float`: `per_request * requests * (1 -
   response_hit_rate)` (exact-match response-cache hits cost nothing), rounded to 2 dp. A hit rate outside `[0, 1]`
   → `ValueError`. The worked example in the book: 3,000 system, 4,000 document, 200 question and 400 answer tokens
   cost $0.0276 per request, $0.0195 with the prefix cached; at 2,000,000 requests a month that's $55,200, $39,000,
   and $27,300 with a 30% response-cache hit rate on top.

## Field notes
Provider-side prompt caching (caching a long shared prefix such as a system prompt or document) is a different,
complementary lever: it cuts input-token cost on every call, not just exact repeats.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch09-llm-application-engineering/ex35-llm-cache-costs`.
- **Expected output:** all 8 tests fail against the starter; when you're done, all 8 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch09-llm-application-engineering/ex35-llm-cache-costs`: all 8 pass.
- **Tests:** `test_cache_costs.py` (8 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The cache is an in-process dictionary and the prices are exercise data. A production cache
  needs a shared store with per-tenant isolation, size limits and invalidation on prompt or model change, and the
  ledger needs a dated price table that includes cache-write and cache-read pricing, reconciled against the
  provider's invoice.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Response cache and cost accounting".
Before I write code, teach me response caching vs provider-side prompt caching, cache keys over canonical JSON,
per-tenant cost accounting and per-request cost models with cache-read pricing. Use short Python examples that are not the exercise solution. Then ask me three
questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch09-llm-application-engineering/ex35-llm-cache-costs/starter.py so that test_cache_costs.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `CachedLLM`,
`CostLedger`, `cost_per_request`, `monthly_cost`. Constraints: Python 3.11+, the standard library and the repo's
fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're
done, run `pytest exercises/ch09-llm-application-engineering/ex35-llm-cache-costs` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Response cache and cost accounting" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Does the cache key include every parameter that changes the output? Could one
tenant receive another tenant's cached answer? Is an unknown model ever priced at zero? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
