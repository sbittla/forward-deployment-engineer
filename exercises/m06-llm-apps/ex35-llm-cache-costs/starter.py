import time


class CachedLLM:
    def __init__(self, llm, ttl_s: float, clock=time.time):
        self.llm = llm
        self.ttl_s = ttl_s
        self.clock = clock

    def complete(self, messages, system=None, tools=None, model=None, **kw):
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
