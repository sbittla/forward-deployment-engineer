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
FAILOVER_STATUS = {429, 503, 529}


class NoRouteError(Exception):
    pass


def estimate_cost(model: Model, in_tokens: int, out_tokens: int) -> float:
    raise NotImplementedError


def route(req: dict, models: list[Model] = MODELS) -> list[str]:
    raise NotImplementedError


def call_with_fallback(clients: dict, order: list[str], messages: list[dict], **kw):
    raise NotImplementedError
