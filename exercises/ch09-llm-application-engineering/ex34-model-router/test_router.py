import json

import pytest

from fde_kit import FakeLLM, LLMResponse


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


HAIKU, SONNET, OPUS = "claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"
TASKS = [[{"role": "user", "content": f"task {i}"}] for i in range(20)]
LATENCY_MS = {HAIKU: 400, SONNET: 1200, OPUS: 2500}


def _task(messages):
    return int(messages[-1]["content"].split()[-1])


def _reply(text='{"ok": true}'):
    return LLMResponse(text=text, input_tokens=2000, output_tokens=300)


def _haiku(m, s, t):                        # cheap: malformed JSON on every fifth (hard) task, one 503
    i = _task(m)
    if i == 19:
        raise APIError(529)
    if i == 12:
        raise APIError(503)
    return _reply('{"ok": tru') if i % 5 == 0 else _reply()


def _sonnet(m, s, t):                       # one timeout, one rate limit
    i = _task(m)
    if i == 19:
        raise APIError(529)
    if i == 3:
        raise TimeoutError("read timed out")
    if i == 7:
        raise APIError(429)
    return _reply()


def _opus(m, s, t):
    if _task(m) == 19:                     # task 19: a provider-wide outage
        raise APIError(529)
    return _reply()


def _clients():
    return {HAIKU: FakeLLM(_haiku), SONNET: FakeLLM(_sonnet), OPUS: FakeLLM(_opus)}


def _accept(resp):
    try:
        return json.loads(resp.text).get("ok") is True
    except ValueError:
        return False


@pytest.mark.parametrize("failure,outcome", [
    (TimeoutError("read timed out"), "timeout"), (APIError(500), "500"), (APIError(502), "502"),
    (APIError(503), "503"), (APIError(504), "504"),
])
def test_fails_over_on_timeout_and_5xx(impl, failure, outcome):
    def broken(*a):
        raise failure

    clients = {"a": FakeLLM(broken), "b": FakeLLM(["fine"])}
    resp, attempts = impl.call_with_fallback(clients, ["a", "b"], [])
    assert resp.text == "fine" and attempts == [("a", outcome), ("b", "ok")]


def test_malformed_reply_fails_over(impl):
    clients = {"a": FakeLLM(['{"ok": tru']), "b": FakeLLM(['{"ok": true}'])}
    resp, attempts = impl.call_with_fallback(clients, ["a", "b"], [], accept=_accept)
    assert resp.model == "b" and attempts == [("a", "malformed"), ("b", "ok")]
    with pytest.raises(impl.MalformedReply) as e:
        impl.call_with_fallback({"a": FakeLLM(["nope"])}, ["a"], [], accept=_accept)
    assert e.value.attempts == [("a", "malformed")]


def test_budget_refuses_before_the_call(impl):
    budget = impl.Budget(limit_usd=0.01)
    clients = {SONNET: FakeLLM([_reply(), _reply()])}
    impl.call_with_fallback(clients, [SONNET], [], budget=budget, in_tokens=2000, max_tokens=300)
    assert budget.spent_usd == pytest.approx(0.007)          # 2,000 in + 300 out on sonnet
    with pytest.raises(impl.BudgetExceeded) as e:          # worst case $0.007 > $0.003 left
        impl.call_with_fallback(clients, [SONNET], [], budget=budget, in_tokens=2000, max_tokens=300)
    assert len(clients[SONNET].calls) == 1 and e.value.attempts == [(SONNET, "budget")]
    assert budget.remaining() == pytest.approx(0.003)


def test_budget_fails_closed(impl):
    # A failover to a pricier model is refused, not silently allowed; an unpriceable model is refused outright.
    def overloaded(*a):
        raise APIError(529)

    budget = impl.Budget(limit_usd=0.01)
    clients = {SONNET: FakeLLM(overloaded), OPUS: FakeLLM([_reply()])}
    with pytest.raises(impl.BudgetExceeded):
        impl.call_with_fallback(clients, [SONNET, OPUS], [], budget=budget, in_tokens=2000, max_tokens=300)
    assert clients[OPUS].calls == [] and budget.spent_usd == 0
    with pytest.raises(impl.BudgetExceeded):
        impl.call_with_fallback({"mystery": FakeLLM(["x"])}, ["mystery"], [], budget=impl.Budget(1.0))


def test_non_retryable_carries_attempts(impl):
    def bad(*a):
        raise APIError(400)

    with pytest.raises(APIError) as e:
        impl.call_with_fallback({"a": FakeLLM(bad)}, ["a"], [])
    assert e.value.attempts == [("a", "400")]


def test_percentile(impl):
    assert impl.percentile([400] * 18 + [1600, 1600], 95) == 1600
    assert impl.percentile([5, 1, 3], 50) == 3 and impl.percentile([7], 95) == 7
    with pytest.raises(ValueError):
        impl.percentile([], 50)


def test_route_comparison_is_reproducible(impl):
    kw = dict(accept=_accept, in_tokens=2000, max_tokens=300)
    cheap_only = impl.simulate(TASKS, [HAIKU], _clients(), LATENCY_MS, **kw)
    cheap_first = impl.simulate(TASKS, [HAIKU, SONNET], _clients(), LATENCY_MS, **kw)
    mid_first = impl.simulate(TASKS, [SONNET, OPUS], _clients(), LATENCY_MS, **kw)
    assert cheap_only == {"tasks": 20, "successes": 14, "success_rate": 0.7, "p50_ms": 400, "p95_ms": 400,
                          "cost_usd": 0.0063, "cost_per_request": 0.000315, "cost_per_success": 0.00045}
    assert cheap_first == {"tasks": 20, "successes": 19, "success_rate": 0.95, "p50_ms": 400, "p95_ms": 1600,
                           "cost_usd": 0.0413, "cost_per_request": 0.002065, "cost_per_success": 0.002174}
    assert mid_first == {"tasks": 20, "successes": 19, "success_rate": 0.95, "p50_ms": 1200, "p95_ms": 3700,
                         "cost_usd": 0.147, "cost_per_request": 0.00735, "cost_per_success": 0.007737}
    assert impl.simulate(TASKS, [HAIKU, SONNET], _clients(), LATENCY_MS, **kw) == cheap_first     # same inputs
