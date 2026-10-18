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
