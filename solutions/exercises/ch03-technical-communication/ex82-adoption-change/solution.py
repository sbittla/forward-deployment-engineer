from collections import defaultdict


def _mean(xs):
    if not xs:
        raise ValueError("every group needs at least one value")
    return sum(xs) / len(xs)


def funnel(events: list[dict]) -> dict:
    invited = {e["user"] for e in events if e["event"] == "invited"}
    activated = {e["user"] for e in events if e["event"] == "login"}
    engaged = {e["user"] for e in events if e["event"] == "query"}
    weeks = defaultdict(set)
    for e in events:
        if e["event"] == "query":
            weeks[e["user"]].add(e["week"])
    habitual = {u for u, w in weeks.items() if len(w) >= 3}
    n = len(invited)
    return {"invited": n, "activated": len(activated), "engaged": len(engaged), "habitual": len(habitual),
            "activation_rate": round(len(activated) / n, 3) if n else 0.0,
            "habit_rate": round(len(habitual) / n, 3) if n else 0.0}


def weekly_retention(events: list[dict], cohort_week: int) -> list[float]:
    first_login = {}
    for e in sorted(events, key=lambda e: e["week"]):
        if e["event"] == "login":
            first_login.setdefault(e["user"], e["week"])
    cohort = {u for u, w in first_login.items() if w == cohort_week}
    if not cohort:
        return []
    active = defaultdict(set)
    for e in events:
        if e["event"] in ("login", "query"):
            active[e["week"]].add(e["user"])
    last = max(e["week"] for e in events)
    return [round(len(cohort & active[w]) / len(cohort), 3) for w in range(cohort_week, last + 1)]


def lagging_teams(events: list[dict], threshold: float = 0.5) -> list[tuple[str, float]]:
    invited, activated = defaultdict(set), defaultdict(set)
    for e in events:
        if e["event"] == "invited":
            invited[e["team"]].add(e["user"])
        elif e["event"] == "login":
            activated[e["team"]].add(e["user"])
    rates = [(t, round(len(activated[t] & users) / len(users), 3)) for t, users in invited.items()]
    return sorted((r for r in rates if r[1] < threshold), key=lambda r: (r[1], r[0]))


def change_plan(lagging: list[tuple[str, float]]) -> list[str]:
    return [f"{team}: executive sponsor message + hands-on workshop + named champion" if rate < 0.25
            else f"{team}: champion office hours + in-app tips" for team, rate in lagging]


def diff_in_diff(pre_treat, post_treat, pre_ctrl, post_ctrl) -> dict:
    t = _mean(post_treat) - _mean(pre_treat)
    c = _mean(post_ctrl) - _mean(pre_ctrl)
    effect = t - c
    return {"treatment_change": round(t, 2), "control_change": round(c, 2), "effect": round(effect, 2),
            "effect_pct": round(effect / _mean(pre_treat) * 100, 2)}
