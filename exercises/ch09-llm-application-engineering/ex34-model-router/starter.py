import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    name: str
    tier: int
    price_in: float   # USD per 1M input tokens
    price_out: float  # USD per 1M output tokens
    p50_ms: int


MODELS = [
    Model("claude-haiku-5-5", 1, 0.10, 0.50, 400),
    Model("claude-sonnet-5-5", 2, 2.00, 10.00, 1200),
    Model("claude-opus-5-5", 3, 4.00, 20.00, 2500),
]
FAILOVER_STATUS = {429, 500, 502, 503, 504, 529}   # overloaded or transient server errors


class NoRouteError(Exception):
    pass


class BudgetExceeded(Exception):
    """The worst-case cost of the next call would exceed the budget, so the call is never made."""


class MalformedReply(Exception):
    """Every model's reply failed the `accept` check."""


@dataclass
class Budget:
    limit_usd: float
    spent_usd: float = 0.0

    def remaining(self) -> float:
        raise NotImplementedError

    def check(self, cost_usd: float) -> None:
        raise NotImplementedError

    def charge(self, cost_usd: float) -> None:
        raise NotImplementedError


def estimate_cost(model: Model, in_tokens: int, out_tokens: int) -> float:
    raise NotImplementedError


def route(req: dict, models: list[Model] = MODELS) -> list[str]:
    raise NotImplementedError


def call_with_fallback(clients: dict, order: list[str], messages: list[dict], *, accept=None, budget=None,
                       in_tokens: int = 0, **kw):
    raise NotImplementedError


def percentile(values: list[float], q: float) -> float:
    raise NotImplementedError


def simulate(tasks: list[list[dict]], order: list[str], clients: dict, latency_ms: dict[str, int], *,
             accept=None, timeout_ms: int = 5000, in_tokens: int = 0, **kw) -> dict:
    raise NotImplementedError
