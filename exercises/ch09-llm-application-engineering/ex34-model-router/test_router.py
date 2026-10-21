import pytest

from fde_kit import FakeLLM


class APIError(Exception):
    def __init__(self, status):
        super().__init__(status)
        self.status = status


def test_cost(impl):
    opus = impl.MODELS[2]
    assert impl.estimate_cost(opus, 10_000, 1_000) == pytest.approx(0.04 + 0.02)


def test_route_cheapest_first(impl):
    req = dict(min_tier=1, max_latency_ms=5000, max_cost_usd=1.0, in_tokens=2000, out_tokens=500)
    assert impl.route(req) == ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"]


def test_route_constraints(impl):
    assert impl.route(dict(min_tier=2, max_latency_ms=2000, max_cost_usd=1, in_tokens=1, out_tokens=1)) == ["claude-sonnet-5-5"]
    with pytest.raises(impl.NoRouteError):
        impl.route(dict(min_tier=3, max_latency_ms=1000, max_cost_usd=1, in_tokens=1, out_tokens=1))
    tight = dict(min_tier=2, max_latency_ms=9999, max_cost_usd=0.01, in_tokens=2000, out_tokens=500)
    # sonnet = 0.004+0.005=0.009 ok ; opus = 0.008+0.01=0.018 too expensive
    assert impl.route(tight) == ["claude-sonnet-5-5"]


def test_fallback_on_overload(impl):
    def overloaded(*a):
        raise APIError(529)

    clients = {"claude-sonnet-5-5": FakeLLM(overloaded), "claude-opus-5-5": FakeLLM(["answer"])}
    resp, attempts = impl.call_with_fallback(clients, ["claude-sonnet-5-5", "claude-opus-5-5"],
                                             [{"role": "user", "content": "hi"}], max_tokens=100)
    assert resp.text == "answer" and resp.model == "claude-opus-5-5"
    assert attempts == [("claude-sonnet-5-5", "529"), ("claude-opus-5-5", "ok")]


def test_non_retryable_propagates(impl):
    def bad(*a):
        raise APIError(400)

    clients = {"a": FakeLLM(bad), "b": FakeLLM(["never"])}
    with pytest.raises(APIError) as e:
        impl.call_with_fallback(clients, ["a", "b"], [])
    assert e.value.status == 400 and clients["b"].calls == []


def test_all_fail(impl):
    def limited(*a):
        raise APIError(429)

    clients = {"a": FakeLLM(limited), "b": FakeLLM(limited)}
    with pytest.raises(APIError):
        impl.call_with_fallback(clients, ["a", "b"], [])
