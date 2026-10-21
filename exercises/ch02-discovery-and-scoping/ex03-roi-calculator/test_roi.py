import math

import pytest

BASE = dict(tasks_per_month=10_000, minutes_saved=4, hourly_cost=45, adoption=0.6,
            in_tokens=6_000, out_tokens=500, price_in_mtok=4.0, price_out_mtok=20.0, calls_per_task=2,
            annual_platform_cost=30_000, one_time_cost=120_000)


def test_labor_savings(impl):
    assert impl.annual_labor_savings(10_000, 4, 45, 0.6) == pytest.approx(216_000)


def test_llm_cost(impl):
    # per call: 6000*4/1e6 + 500*20/1e6 = 0.024 + 0.01 = 0.034 ; *2 calls *10k *12
    assert impl.annual_llm_cost(10_000, 6_000, 500, 4.0, 20.0, 2) == pytest.approx(8_160)


def test_payback(impl):
    assert impl.payback_months(120_000, 10_000) == 12
    assert math.isinf(impl.payback_months(1, 0))
    assert math.isinf(impl.payback_months(1, -5))


def test_summary(impl):
    s = impl.roi_summary(**BASE)
    assert s["annual_savings"] == 216_000
    assert s["annual_llm_cost"] == 8_160
    assert s["annual_run_cost"] == 38_160
    assert s["annual_net"] == 177_840
    assert s["roi_pct"] == round((177_840 - 120_000) / (120_000 + 38_160) * 100, 2)
    assert s["payback_months"] == round(120_000 / (177_840 / 12), 2)


def test_sensitivity(impl):
    rows = impl.sensitivity(BASE, "adoption", [0.5, 1.0])
    assert rows[1] == (1.0, 177_840)
    assert rows[0][1] == 216_000 * 0.5 - 38_160
    assert BASE["adoption"] == 0.6  # must not mutate inputs


NORTHWIND = dict(tasks_per_month=40_000, minutes_saved=4, hourly_cost=45, adoption=0.6,
                 in_tokens=6_000, out_tokens=400, price_in_mtok=3.0, price_out_mtok=15.0, calls_per_task=2,
                 annual_platform_cost=120_000, one_time_cost=250_000)


def test_sensitivity_scales_several_params_together(impl):
    # the book's token-price column: input and output price move together
    rows = impl.sensitivity(NORTHWIND, ("price_in_mtok", "price_out_mtok"), [0.25, 0.5, 1.0, 2.0])
    assert rows == [(0.25, 738_240), (0.5, 732_480), (1.0, 720_960), (2.0, 697_920)]
    assert NORTHWIND["price_in_mtok"] == 3.0 and NORTHWIND["price_out_mtok"] == 15.0


def test_edge_cases(impl):
    assert impl.payback_months(1000, 0) == float("inf") and impl.payback_months(1000, -5) == float("inf")
    assert impl.annual_llm_cost(0, 100, 100, 3, 15) == 0.0
    assert impl.annual_labor_savings(1000, 5, 60, adoption=0.0) == 0.0
