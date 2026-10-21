import pytest

BASE_LEN = [20 + (i * 7) % 80 for i in range(200)]
BASELINE = {"input_len": BASE_LEN, "intents": {"billing": 40, "account": 30, "bug": 30}, "judge_pass": 0.9}


def rec(i, **kw):
    r = {"input_len": 20 + (i * 11) % 80, "intent": ["billing", "account", "bug"][i % 3] if i % 10 else "billing",
         "judge_pass": i % 10 != 0, "refused": False, "latency_ms": 1000 + i, "cost": 0.02}
    r.update(kw)
    return r


def test_quantile_edges_and_p95(impl):
    assert impl.quantile_edges(list(range(10)), 4) == [2, 5, 7]
    assert impl.p95(list(range(1, 101))) == 95 and impl.p95([5]) == 5 and impl.p95([3, 1, 2]) == 3


def test_psi_numeric(impl):
    assert impl.psi(BASE_LEN, BASE_LEN) == 0.0
    assert impl.psi(BASE_LEN, [20 + (i * 11) % 80 for i in range(100)]) == 0.001
    assert impl.psi(BASE_LEN, [60 + (i * 7) % 120 for i in range(100)]) == 4.7069
    with pytest.raises(ValueError):
        impl.psi([], [1.0])


def test_category_psi_and_levels(impl):
    b = {"billing": 50, "account": 30, "bug": 20}
    assert impl.category_psi(b, {"billing": 48, "account": 32, "bug": 20}) == 0.0021
    assert impl.category_psi(b, {"billing": 20, "account": 20, "bug": 20, "outage": 40}) == 3.6322   # new intent
    assert impl.category_psi(BASELINE["intents"], {"billing": 60, "account": 20, "bug": 20}) == 0.1622
    assert [impl.drift_level(x) for x in (0.05, 0.1, 0.1622, 0.25, 4.0)] == ["stable", "watch", "watch", "drift", "drift"]
    with pytest.raises(ValueError):
        impl.category_psi({}, {"a": 1})


def test_healthy_window_is_quiet(impl):
    assert impl.check_window(BASELINE, [rec(i) for i in range(60)]) == []


def test_too_few_samples(impl):
    alerts = impl.check_window(BASELINE, [rec(i) for i in range(10)])
    assert alerts == [{"metric": "samples", "level": "info", "value": 10,
                       "message": "only 10 records; need 50 before alerting"}]


def test_degraded_window(impl):
    bad = [rec(i, judge_pass=i % 4 != 0, refused=i % 12 == 0, latency_ms=1000 + 100 * i, input_len=60 + (i * 7) % 120)
           for i in range(60)]
    alerts = impl.check_window(BASELINE, bad)
    assert [(a["metric"], a["level"], a["value"]) for a in alerts] == [
        ("input_len_psi", "drift", 4.6268), ("judge_pass", "page", 0.75), ("refusal_rate", "page", 0.0833),
        ("p95_latency_ms", "page", 6600)]


def test_intent_shift_cost_and_unjudged(impl):
    intents = ["billing"] * 36 + ["account"] * 12 + ["bug"] * 12
    window = [rec(i, intent=intents[i], cost=0.15, judge_pass=None if i % 2 else False) for i in range(60)]
    alerts = {a["metric"]: (a["level"], a["value"]) for a in impl.check_window(BASELINE, window)}
    assert alerts == {"intent_psi": ("watch", 0.1622), "cost_per_conv": ("watch", 0.15)}  # 30 judged < 50: no judge alert
    strict = impl.Thresholds(min_samples=20)
    assert impl.check_window(BASELINE, window, strict)[1]["metric"] == "judge_pass"


def test_sampling_is_deterministic(impl):
    recs = [{"id": f"conv-{i}"} for i in range(20)]
    assert impl.sample_for_review(recs, 0.2) == ["conv-2", "conv-11", "conv-14", "conv-17"]
    assert impl.sample_for_review(recs, 0.2) == impl.sample_for_review(list(recs), 0.2)
    assert impl.sample_for_review(recs, 0.0, always=lambda r: r["id"].endswith("7")) == ["conv-7", "conv-17"]
    assert len(impl.sample_for_review(recs, 1.0)) == 20
    with pytest.raises(ValueError):
        impl.sample_for_review(recs, 1.5)
