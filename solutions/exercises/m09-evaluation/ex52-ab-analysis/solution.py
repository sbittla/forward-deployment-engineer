import math
import random
import statistics


def _mean(xs):
    return sum(xs) / len(xs)


def lift(control: list[int], variant: list[int]) -> float:
    return _mean(variant) - _mean(control)


def bootstrap_ci(control, variant, n=2000, alpha=0.05, seed=0) -> tuple[float, float]:
    rng = random.Random(seed)
    lifts = sorted(
        _mean(rng.choices(variant, k=len(variant))) - _mean(rng.choices(control, k=len(control)))
        for _ in range(n)
    )

    def q(p):
        return lifts[min(n - 1, int(p * n))]

    return round(q(alpha / 2), 4), round(q(1 - alpha / 2), 4)


def z_test(control, variant) -> float:
    n1, n2 = len(control), len(variant)
    p1, p2 = _mean(control), _mean(variant)
    pooled = (sum(control) + sum(variant)) / (n1 + n2)
    var = pooled * (1 - pooled) * (1 / n1 + 1 / n2)
    if var == 0:
        return 1.0
    z = (p2 - p1) / math.sqrt(var)
    return round(math.erfc(abs(z) / math.sqrt(2)), 4)


def _z(p: float) -> float:
    return statistics.NormalDist().inv_cdf(p)


def sample_size(p_base: float, mde: float, alpha: float = 0.05, power: float = 0.8) -> int:
    z_a = 1.959964 if alpha == 0.05 else _z(1 - alpha / 2)
    z_b = 0.841621 if power == 0.8 else _z(power)
    p1, p2 = p_base, p_base + mde
    pbar = (p1 + p2) / 2
    num = (z_a * math.sqrt(2 * pbar * (1 - pbar)) + z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / mde ** 2)


def decide(control, variant, **kw) -> str:
    lo, hi = bootstrap_ci(control, variant, **kw)
    if lo > 0 and z_test(control, variant) < 0.05:
        return "ship"
    if hi < 0:
        return "harmful"
    return "inconclusive"
