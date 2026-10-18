"""Adoption funnel, lagging teams and difference-in-differences impact."""
from collections import defaultdict


def _mean(xs):
    return sum(xs) / len(xs)


def funnel(events: list[dict]) -> dict:
    invited = {e["user"] for e in events if e["event"] == "invited"}
    activated = {e["user"] for e in events if e["event"] == "login"}
    weeks = defaultdict(set)
    for e in events:
        if e["event"] == "query":
            weeks[e["user"]].add(e["week"])
    habitual = {u for u, w in weeks.items() if len(w) >= 3}
    n = len(invited)
    return {"invited": n, "activated": len(activated), "habitual": len(habitual),
            "activation_rate": round(len(activated) / n, 3), "habit_rate": round(len(habitual) / n, 3)}


def lagging_teams(events: list[dict], threshold: float = 0.5) -> list[tuple[str, float]]:
    inv, act = defaultdict(set), defaultdict(set)
    for e in events:
        if e["event"] == "invited":
            inv[e["team"]].add(e["user"])
        elif e["event"] == "login":
            act[e["team"]].add(e["user"])
    rates = [(t, round(len(act[t] & u) / len(u), 3)) for t, u in inv.items()]
    return sorted((r for r in rates if r[1] < threshold), key=lambda r: (r[1], r[0]))


def diff_in_diff(pre_t, post_t, pre_c, post_c) -> dict:
    t, c = _mean(post_t) - _mean(pre_t), _mean(post_c) - _mean(pre_c)
    effect = t - c
    return {"treatment_change": round(t, 2), "control_change": round(c, 2), "effect": round(effect, 2),
            "effect_pct": round(effect / _mean(pre_t) * 100, 2)}
