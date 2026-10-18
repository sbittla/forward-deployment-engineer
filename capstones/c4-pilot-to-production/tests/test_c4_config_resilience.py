import pytest

from fde_kit import FakeLLM, LLMResponse

PACKAGE = "pilot"
ENV = {"PILOT_API_TOKENS": "tok-a, tok-b", "PILOT_LLM_ENDPOINT": "https://llm-gateway.logistics.example",
       "PILOT_EGRESS_ALLOWLIST": "llm-gateway.logistics.example", "HTTPS_PROXY": "http://proxy:3128"}


class APIError(Exception):
    def __init__(self, status, retry_after=None):
        super().__init__(status)
        self.status = status
        if retry_after is not None:
            self.retry_after = retry_after


class Clock:
    t = 0.0

    def __call__(self):
        return self.t


def test_settings(cap):
    s = cap.load_settings(ENV)
    assert [t.reveal() for t in s.api_tokens] == ["tok-a", "tok-b"] and s.https_proxy == "http://proxy:3128"
    assert "tok-a" not in repr(s) and s.redacted()["api_tokens"] == "2 token(s)"


def test_settings_errors_aggregated(cap):
    with pytest.raises(cap.ConfigError) as e:
        cap.load_settings({"PILOT_LLM_ENDPOINT": "http://insecure", "PILOT_TIMEOUT_S": "999"})
    assert len(e.value.errors) == 3
    with pytest.raises(cap.ConfigError) as e:
        cap.load_settings({**ENV, "PILOT_EGRESS_ALLOWLIST": "other.example"})
    assert "not in PILOT_EGRESS_ALLOWLIST" in e.value.errors[0]


def test_retry_then_fallback(cap):
    sleeps = []

    def overloaded(m, s, t):
        raise APIError(529)

    primary, fallback = FakeLLM(overloaded), FakeLLM(["fallback summary"])
    llm = cap.ResilientLLM(primary, fallback, model="big", fallback_model="small", sleep=sleeps.append, rng=lambda: 1)
    resp = llm.complete([{"role": "user", "content": "x"}])
    assert resp.text == "fallback summary" and resp.model == "small"
    assert len(primary.calls) == 3 and sleeps == [0.5, 1.0] and llm.breaker_state == "closed"


def test_retry_after_and_non_retryable(cap):
    sleeps, calls = [], {"n": 0}

    def flaky(m, s, t):
        calls["n"] += 1
        if calls["n"] == 1:
            raise APIError(429, retry_after=7)
        return LLMResponse(text="ok")

    assert cap.ResilientLLM(FakeLLM(flaky), sleep=sleeps.append).complete([]).text == "ok" and sleeps == [7]

    def bad_request(m, s, t):
        raise APIError(400)

    llm = cap.ResilientLLM(FakeLLM(bad_request), FakeLLM(["never"]), sleep=lambda s: None)
    with pytest.raises(APIError):
        llm.complete([])


def test_breaker_opens_and_recovers(cap):
    clk = Clock()
    state = {"fail": True}

    def upstream(m, s, t):
        if state["fail"]:
            raise APIError(500)
        return LLMResponse(text="ok")

    primary = FakeLLM(upstream)
    llm = cap.ResilientLLM(primary, max_retries=0, breaker_threshold=2, reset_timeout=30, clock=clk, sleep=lambda s: None)
    for _ in range(2):
        with pytest.raises(APIError):
            llm.complete([])
    assert llm.breaker_state == "open"
    with pytest.raises(cap.CircuitOpen):
        llm.complete([])
    assert len(primary.calls) == 2
    clk.t = 31
    state["fail"] = False
    assert llm.complete([]).text == "ok" and llm.breaker_state == "closed"
