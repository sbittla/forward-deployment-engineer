from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    name: str
    tier: int
    price_in: float
    price_out: float
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
    return in_tokens * model.price_in / 1e6 + out_tokens * model.price_out / 1e6


def route(req: dict, models: list[Model] = MODELS) -> list[str]:
    eligible = [
        m for m in models
        if m.tier >= req["min_tier"] and m.p50_ms <= req["max_latency_ms"]
        and estimate_cost(m, req["in_tokens"], req["out_tokens"]) <= req["max_cost_usd"]
    ]
    if not eligible:
        raise NoRouteError(f"no model satisfies {req}")
    eligible.sort(key=lambda m: (estimate_cost(m, req["in_tokens"], req["out_tokens"]), m.p50_ms))
    return [m.name for m in eligible]


def call_with_fallback(clients: dict, order: list[str], messages: list[dict], **kw):
    attempts, last = [], None
    for name in order:
        try:
            resp = clients[name].complete(messages, model=name, **kw)
        except Exception as exc:
            status = getattr(exc, "status", None)
            if status not in FAILOVER_STATUS:
                raise
            attempts.append((name, str(status)))
            last = exc
            continue
        attempts.append((name, "ok"))
        return resp, attempts
    raise last
