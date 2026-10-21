import math
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
        return self.limit_usd - self.spent_usd

    def check(self, cost_usd: float) -> None:
        if self.spent_usd + cost_usd > self.limit_usd + 1e-12:
            raise BudgetExceeded(f"${cost_usd:.6f} needed, ${self.remaining():.6f} left of ${self.limit_usd}")

    def charge(self, cost_usd: float) -> None:
        self.spent_usd += cost_usd


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


def call_with_fallback(clients: dict, order: list[str], messages: list[dict], *, accept=None, budget=None,
                       in_tokens: int = 0, **kw):
    """Try models in order. Fail over on overload or transient server errors, on timeouts and on replies `accept`
    rejects; anything else propagates. With a budget, refuse (fail closed) before any call whose worst-case cost
    (in_tokens plus max_tokens) doesn't fit, and charge every reply that comes back, accepted or not.
    Every exception raised carries `.attempts`."""
    attempts, last = [], None
    by_name = {m.name: m for m in MODELS}
    for name in order:
        if budget is not None:
            if name not in by_name:
                last = BudgetExceeded(f"cannot price {name!r}; refusing under a budget")
                break
            worst = estimate_cost(by_name[name], in_tokens, kw.get("max_tokens", 1024))
            try:
                budget.check(worst)
            except BudgetExceeded as exc:
                attempts.append((name, "budget"))
                last = exc
                break
        try:
            resp = clients[name].complete(messages, model=name, **kw)
        except TimeoutError as exc:
            attempts.append((name, "timeout"))
            last = exc
            continue
        except Exception as exc:
            status = getattr(exc, "status", None)
            if status not in FAILOVER_STATUS:
                attempts.append((name, str(status)))
                exc.attempts = attempts
                raise
            attempts.append((name, str(status)))
            last = exc
            continue
        if budget is not None:
            budget.charge(estimate_cost(by_name[name], resp.input_tokens, resp.output_tokens))
        if accept is not None and not accept(resp):
            attempts.append((name, "malformed"))
            last = MalformedReply(f"{name} reply failed validation")
            continue
        attempts.append((name, "ok"))
        return resp, attempts
    last.attempts = attempts
    raise last


def percentile(values: list[float], q: float) -> float:
    """Nearest-rank percentile: the smallest value with at least q% of values at or below it."""
    if not values:
        raise ValueError("no values")
    ranked = sorted(values)
    return ranked[max(0, math.ceil(q / 100 * len(ranked)) - 1)]


def simulate(tasks: list[list[dict]], order: list[str], clients: dict, latency_ms: dict[str, int], *,
             accept=None, timeout_ms: int = 5000, in_tokens: int = 0, **kw) -> dict:
    """Replay a fixed task set through one route with fixed per-model latencies (a simulated clock, not wall time).
    A task's latency is the sum over its attempts; a timed-out attempt costs `timeout_ms`."""
    budget = Budget(math.inf)
    latencies, successes = [], 0
    for messages in tasks:
        try:
            _, attempts = call_with_fallback(clients, order, messages, accept=accept, budget=budget,
                                             in_tokens=in_tokens, **kw)
            successes += 1
        except Exception as exc:
            attempts = getattr(exc, "attempts", [])
        latencies.append(sum(timeout_ms if outcome == "timeout" else latency_ms[name] for name, outcome in attempts))
    n, cost = len(tasks), budget.spent_usd
    return {"tasks": n, "successes": successes, "success_rate": round(successes / n, 4) if n else 0.0,
            "p50_ms": percentile(latencies, 50) if n else 0, "p95_ms": percentile(latencies, 95) if n else 0,
            "cost_usd": round(cost, 6), "cost_per_request": round(cost / n, 6) if n else 0.0,
            "cost_per_success": round(cost / successes, 6) if successes else None}
