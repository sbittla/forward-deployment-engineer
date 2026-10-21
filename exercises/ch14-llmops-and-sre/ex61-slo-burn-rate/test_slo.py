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


def test_page_fires_at_exactly_14_4(impl):
    slo = impl.SLO(target=0.99)

    def batch(ts, n, bad):
        return [(ts, 503 if i < bad else 200, 100) for i in range(n)]

    at = batch(NOW - 3000, 250, 36) + batch(NOW - 60, 250, 36)        # 72 / 500 bad: burn 14.4 on 1 h and 5 min
    assert slo.burn_rate(at, NOW, 3600) == 14.4 and slo.alerts(at, NOW) == ["page"]
    below = batch(NOW - 3000, 250, 36) + batch(NOW - 60, 250, 35)     # 1 h burn 14.2: a ticket, not a page
    assert slo.alerts(below, NOW) == ["ticket"]


def test_canary_rollback_on_burn(impl):
    slo = impl.SLO(target=0.995)                                      # budget 0.5%
    healthy = traffic(NOW - 3600, NOW, 6, bad_every=500)              # 600 requests, 2 bad: burn 0.67
    assert slo.canary_action(healthy, NOW) == "promote"
    burning = traffic(NOW - 3600, NOW, 6, bad_every=50)               # 12 bad: burn 4.0 > 2.0
    assert slo.canary_action(burning, NOW) == "rollback"
    assert slo.canary_action(traffic(NOW - 600, NOW, 6), NOW) == "wait"   # 100 requests, all good
    early_bad = traffic(NOW - 600, NOW, 6, bad_every=10)              # 10 bad > 2.0 x 0.005 x 500 = 5
    assert slo.canary_action(early_bad, NOW) == "rollback"


def _clock(t):
    return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d}"


def test_worked_example_alert_times(impl):
    # Chapter 14's Table 14.7, on a simulated clock: 1 request a second from 07:00, 2 a second from the 08:30 peak,
    # when 15% of requests start returning 503 until the rollback. Synthetic traffic, not a measurement.
    slo, H = impl.SLO(), 3600                               # 99.5% over 30 days; streamed answers, 3,000 ms
    start, peak = 7 * H, 8 * H + 30 * 60

    def gen(rollback=None):
        out, t, i = [], start, 0
        while t < 10 * H:
            bad = peak <= t and (rollback is None or t < rollback) and i % 20 < 3
            out.append((t, 503 if bad else 200, 1200))
            t += 1 / (2 if t >= peak else 1)
            i += 1
        return out

    def first(reqs, t, cond):
        while not cond(slo.alerts(reqs, t)):
            t += 20
            assert t < 10 * H, "the expected alert state never came"
        return t

    reqs = gen()
    ticket = first(reqs, peak, lambda a: a == ["ticket"])
    page = first(reqs, ticket, lambda a: a == ["page"])
    assert (_clock(ticket), _clock(page)) == ("08:41:20", "08:49:00")
    rollback = page + 12 * 60
    clears = first(gen(rollback), rollback, lambda a: "page" not in a)
    assert (_clock(rollback), _clock(clears)) == ("09:01:00", "09:03:40")
