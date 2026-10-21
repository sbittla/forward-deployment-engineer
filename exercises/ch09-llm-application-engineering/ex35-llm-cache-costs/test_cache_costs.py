import pytest

from fde_kit import FakeLLM, LLMResponse, ToolCall

PRICES = {"claude-sonnet-5-5": (2.0, 10.0), "claude-haiku-5-5": (0.10, 0.50)}


class Clock:
    t = 0.0

    def __call__(self):
        return self.t


def msgs(q):
    return [{"role": "user", "content": q}]


def test_cache_hits_and_ttl(impl):
    clk = Clock()
    llm = FakeLLM(lambda m, s, t: f"answer to {m[-1]['content']}")
    c = impl.CachedLLM(llm, ttl_s=60, clock=clk)
    a = c.complete(msgs("reset password"), system="S", model="m")
    b = c.complete(msgs("reset password"), system="S", model="m")
    assert a.text == b.text and len(llm.calls) == 1
    c.complete(msgs("reset password"), system="OTHER", model="m")
    assert len(llm.calls) == 2
    clk.t = 61
    c.complete(msgs("reset password"), system="S", model="m")
    assert len(llm.calls) == 3
    assert c.stats() == {"hits": 1, "misses": 3, "hit_rate": 0.25}


def test_key_is_canonical(impl):
    llm = FakeLLM(lambda m, s, t: "x")
    c = impl.CachedLLM(llm, ttl_s=60, clock=Clock())
    c.complete([{"content": "q", "role": "user"}], max_tokens=10)
    c.complete([{"role": "user", "content": "q"}], max_tokens=10)
    c.complete([{"role": "user", "content": "q"}], max_tokens=20)
    assert len(llm.calls) == 2


def test_tool_calls_not_cached(impl):
    llm = FakeLLM(lambda m, s, t: LLMResponse(tool_calls=[ToolCall("1", "lookup", {})]))
    c = impl.CachedLLM(llm, ttl_s=60, clock=Clock())
    c.complete(msgs("q"))
    c.complete(msgs("q"))
    assert len(llm.calls) == 2


def test_empty_stats(impl):
    assert impl.CachedLLM(FakeLLM([]), 1).stats() == {"hits": 0, "misses": 0, "hit_rate": 0.0}


def test_ledger(impl):
    led = impl.CostLedger(PRICES)
    r1 = LLMResponse(text="a", input_tokens=10_000, output_tokens=1_000, model="claude-sonnet-5-5")
    r2 = LLMResponse(text="b", input_tokens=100_000, output_tokens=10_000, model="claude-haiku-5-5")
    led.record("acme", r1)
    led.record("acme", r1, cached=True)
    led.record("globex", r2)
    t = led.by_tenant()
    assert t["acme"] == {"requests": 2, "cost_usd": pytest.approx(0.03)}
    assert t["globex"]["cost_usd"] == pytest.approx(0.015)
    assert led.over_budget({"acme": 0.03, "globex": 0.01}) == ["globex"]


def test_unknown_model(impl):
    with pytest.raises(KeyError):
        impl.CostLedger(PRICES).record("x", LLMResponse(model="mystery", input_tokens=1, output_tokens=1))


def test_cost_per_request_worked_example(impl):
    assert impl.cost_per_request(3000, 4000, 200, 400) == pytest.approx(0.0276)
    assert impl.cost_per_request(3000, 4000, 200, 400, cached_prefix=True) == pytest.approx(0.0195)
    assert impl.cost_per_request(3000, 4000, 200, 400, cached_prefix=True, cache_read=0.25) == pytest.approx(0.02085)
    assert impl.cost_per_request(1000, 0, 0, 0, price_in=2.0, cache_read=0.0) == pytest.approx(0.002)
    with pytest.raises(ValueError):
        impl.cost_per_request(3000, -1, 200, 400)


def test_monthly_projection(impl):
    plain = impl.cost_per_request(3000, 4000, 200, 400)
    cached = impl.cost_per_request(3000, 4000, 200, 400, cached_prefix=True)
    assert impl.monthly_cost(plain, 2_000_000) == 55200.0
    assert impl.monthly_cost(cached, 2_000_000) == 39000.0
    assert impl.monthly_cost(cached, 2_000_000, response_hit_rate=0.3) == 27300.0
    assert impl.monthly_cost(cached, 2_000_000, response_hit_rate=1.0) == 0.0
    for bad in (-0.1, 1.5):
        with pytest.raises(ValueError):
            impl.monthly_cost(cached, 2_000_000, response_hit_rate=bad)


def test_key_includes_tenant_and_entitlements(impl):
    # Identical prompts with a different tenant or entitlement scope must not share an entry, even though nothing in
    # the prompt names the tenant.
    llm = FakeLLM(lambda m, s, t: "Claims over $10k: 3")
    c = impl.CachedLLM(llm, ttl_s=60, clock=Clock())
    q = msgs("How many of my team's claims are over $10k?")
    c.complete(q, system="S", model="m", tenant="acme", entitlements=["claims:read"])
    c.complete(q, system="S", model="m", tenant="globex", entitlements=["claims:read"])
    c.complete(q, system="S", model="m", tenant="acme", entitlements=["claims:read", "claims:reserves"])
    assert len(llm.calls) == 3
    c.complete(q, system="S", model="m", tenant="acme", entitlements=["claims:reserves", "claims:read"])
    c.complete(q, system="S", model="m", tenant="acme", entitlements=["claims:read"])
    assert len(llm.calls) == 3 and c.stats()["hits"] == 2         # same scope in any order: a hit
    c.complete(q, system="S", model="m")                          # no scope is its own scope
    assert len(llm.calls) == 4


def test_cross_tenant_requests_do_not_share_entries(impl):
    # Cross-tenant leak check: the same question under each tenant's own system prompt must not hit the other's entry.
    llm = FakeLLM(lambda m, s, t: f"{s} says: your limit is private")
    c = impl.CachedLLM(llm, ttl_s=60, clock=Clock())
    acme = c.complete(msgs("What is my claim limit?"), system="Tenant: acme", model="m")
    globex = c.complete(msgs("What is my claim limit?"), system="Tenant: globex", model="m")
    assert "acme" not in globex.text and len(llm.calls) == 2
    assert c.complete(msgs("What is my claim limit?"), system="Tenant: acme", model="m").text == acme.text
