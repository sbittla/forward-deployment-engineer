import math
import random
import statistics


def lift(control: list[int], variant: list[int]) -> float:
    raise NotImplementedError


def bootstrap_ci(control, variant, n=2000, alpha=0.05, seed=0) -> tuple[float, float]:
    raise NotImplementedError


def z_test(control, variant) -> float:
    raise NotImplementedError


def sample_size(p_base: float, mde: float, alpha: float = 0.05, power: float = 0.8) -> int:
    raise NotImplementedError


def decide(control, variant, **kw) -> str:
    raise NotImplementedError
