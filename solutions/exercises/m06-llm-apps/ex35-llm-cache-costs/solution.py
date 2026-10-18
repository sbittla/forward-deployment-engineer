import hashlib
import json
import time
from collections import defaultdict


class CachedLLM:
    def __init__(self, llm, ttl_s: float, clock=time.time):
        self.llm = llm
        self.ttl_s = ttl_s
        self.clock = clock
        self._store: dict[str, tuple[float, object]] = {}
        self._hits = self._misses = 0

    @staticmethod
    def _key(**parts) -> str:
        return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()

    def complete(self, messages, system=None, tools=None, model=None, **kw):
        key = self._key(model=model, system=system, messages=messages, tools=tools, kw=kw)
        now = self.clock()
        hit = self._store.get(key)
        if hit and now - hit[0] < self.ttl_s:
            self._hits += 1
            return hit[1]
        self._misses += 1
        resp = self.llm.complete(messages, system=system, tools=tools, model=model, **kw)
        if resp.stop_reason == "end_turn" and not resp.tool_calls:
            self._store[key] = (now, resp)
        return resp

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {"hits": self._hits, "misses": self._misses, "hit_rate": round(self._hits / total, 3) if total else 0.0}


class CostLedger:
    def __init__(self, prices: dict[str, tuple[float, float]]):
        self.prices = prices
        self._t = defaultdict(lambda: {"requests": 0, "cost_usd": 0.0})

    def record(self, tenant: str, response, cached: bool = False) -> None:
        p_in, p_out = self.prices[response.model]  # KeyError on unknown models is deliberate
        row = self._t[tenant]
        row["requests"] += 1
        if not cached:
            row["cost_usd"] += response.input_tokens * p_in / 1e6 + response.output_tokens * p_out / 1e6

    def by_tenant(self) -> dict:
        return {t: {"requests": r["requests"], "cost_usd": round(r["cost_usd"], 6)} for t, r in self._t.items()}

    def over_budget(self, budgets: dict[str, float]) -> list[str]:
        spend = self.by_tenant()
        return sorted(t for t, limit in budgets.items() if spend.get(t, {"cost_usd": 0})["cost_usd"] > limit)
