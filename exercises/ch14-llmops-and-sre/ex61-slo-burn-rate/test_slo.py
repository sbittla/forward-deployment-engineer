import pytest

NOW = 100 * 3600


def traffic(start, end, every, bad_every=None, slow_every=None):
    """Requests at timestamps in (start, end], matching the SLO window semantics."""
    reqs = []
    for i, ts in enumerate(range(start + every, end + 1, every)):
        status, lat = 200, 300
        if bad_every and i % bad_every == 0:
            status = 503
        if slow_every and i % slow_every == 0:
            lat = 5000
        reqs.append((ts, status, lat))
    return reqs


def test_budget_and_sli(impl):
    slo = impl.SLO(target=0.99)
    assert slo.error_budget == pytest.approx(0.01)
    reqs = traffic(NOW - 1000, NOW, 10, bad_every=10)   # 100 reqs, 10 bad
    assert slo.sli(reqs, NOW, 1000) == pytest.approx(0.9)
    assert slo.burn_rate(reqs, NOW, 1000) == 10.0
    assert slo.sli([], NOW, 60) is None and slo.burn_rate([], NOW, 60) == 0.0


def test_latency_counts_as_bad(impl):
    slo = impl.SLO(target=0.99, latency_threshold_ms=3000)
    reqs = traffic(NOW - 100, NOW, 1, slow_every=4)      # 25% slow
    assert slo.sli(reqs, NOW, 100) == pytest.approx(0.75)


def test_window_bounds(impl):
    slo = impl.SLO()
    reqs = [(NOW - 60, 500, 1), (NOW - 59, 200, 1), (NOW, 200, 1)]
    assert slo.sli(reqs, NOW, 60) == 1.0  # ts == now-60 excluded


def test_page(impl):
    slo = impl.SLO(target=0.999)
    reqs = traffic(NOW - 6 * 3600, NOW, 5) + traffic(NOW - 3600, NOW, 5, bad_every=20)  # 5% errors last hour
    assert slo.alerts(reqs, NOW) == ["page"]


def test_ticket_not_page(impl):
    slo = impl.SLO(target=0.999)
    # 0.8% errors for 6h -> burn 8 on 6h and 30m, below 14.4
    reqs = traffic(NOW - 6 * 3600, NOW, 2, bad_every=125)
    assert slo.alerts(reqs, NOW) == ["ticket"]


def test_short_spike_no_page(impl):
    slo = impl.SLO(target=0.999)
    healthy = traffic(NOW - 3600, NOW - 300, 1)
    spike = traffic(NOW - 300, NOW, 1, bad_every=10)
    # 5m burn is high but 1h burn is ~ (30/3600)/0.001 = 8.3 < 14.4
    assert "page" not in slo.alerts(healthy + spike, NOW)


def test_budget_remaining(impl):
    slo = impl.SLO(target=0.99)
    reqs = traffic(NOW - 1000, NOW, 1, bad_every=200)  # 5 bad / 1000 -> half budget used
    assert slo.budget_remaining(reqs, NOW) == 0.5
    assert slo.budget_remaining([], NOW) == 1.0
