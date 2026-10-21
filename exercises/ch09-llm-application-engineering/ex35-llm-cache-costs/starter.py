import time


class CachedLLM:
    def __init__(self, llm, ttl_s: float, clock=time.time):
        self.llm = llm
        self.ttl_s = ttl_s
        self.clock = clock

    def complete(self, messages, system=None, tools=None, model=None, tenant=None, entitlements=None, **kw):
        raise NotImplementedError

    def stats(self) -> dict:
        raise NotImplementedError


class CostLedger:
    def __init__(self, prices: dict[str, tuple[float, float]]):
        self.prices = prices

    def record(self, tenant: str, response, cached: bool = False) -> None:
        raise NotImplementedError

    def by_tenant(self) -> dict:
        raise NotImplementedError

    def over_budget(self, budgets: dict[str, float]) -> list[str]:
        raise NotImplementedError


def cost_per_request(system: int, docs: int, question: int, output: int,
                     price_in: float = 3.0, price_out: float = 15.0,
                     cached_prefix: bool = False, cache_read: float = 0.1) -> float:
    raise NotImplementedError


def monthly_cost(per_request: float, requests: int, response_hit_rate: float = 0.0) -> float:
    raise NotImplementedError
