import math

import pytest


def group(successes, n):
    return [1] * successes + [0] * (n - successes)


def test_lift(impl):
    assert impl.lift(group(50, 100), group(60, 100)) == pytest.approx(0.10)


def test_z_test_known_value(impl):
    # 500/1000 vs 550/1000: pooled p=.525, se=sqrt(.525*.475*(2/1000)) ; z=0.05/se
    p = 0.525
    z = 0.05 / math.sqrt(p * (1 - p) * 2 / 1000)
    assert impl.z_test(group(500, 1000), group(550, 1000)) == round(math.erfc(z / math.sqrt(2)), 4)
    assert impl.z_test([1, 1], [1, 1]) == 1.0


def test_bootstrap_deterministic_and_covers(impl):
    c, v = group(712, 1000), group(740, 1000)
    ci1 = impl.bootstrap_ci(c, v, n=1000, seed=42)
    ci2 = impl.bootstrap_ci(c, v, n=1000, seed=42)
    assert ci1 == ci2 and ci1[0] < 0.028 < ci1[1]
    assert ci1[1] - ci1[0] == pytest.approx(0.08, abs=0.02)


def test_sample_size(impl):
    n = impl.sample_size(0.712, 0.03)
    assert 3000 < n < 3600
    assert impl.sample_size(0.5, 0.1) == 388
    assert impl.sample_size(0.5, 0.1, power=0.9) > 388


def test_decide(impl):
    assert impl.decide(group(712, 1000), group(740, 1000), n=500, seed=1) == "inconclusive"
    assert impl.decide(group(7120, 10000), group(7400, 10000), n=500, seed=1) == "ship"
    assert impl.decide(group(7400, 10000), group(7100, 10000), n=500, seed=1) == "harmful"


def test_empty_groups(impl):
    for fn in (impl.lift, impl.bootstrap_ci, impl.z_test, impl.decide):
        with pytest.raises(ValueError):
            fn([], [1, 0, 1])
    assert impl.z_test([0, 0, 0], [0, 0, 0]) == 1.0
