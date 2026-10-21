"""Baseline plan (PERT + critical path), forecast from actual progress, and workstream RAG status."""
import json
import math
from pathlib import Path

Z90 = 1.2816


def load_json(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def expected(t: dict) -> float:
    return (t["o"] + 4 * t["m"] + t["p"]) / 6


def _order(tasks):
    ids = {t["id"] for t in tasks}
    for t in tasks:
        if set(t["deps"]) - ids:
            raise ValueError(f"{t['id']} depends on unknown tasks")
    done, out = set(), []
    while len(out) < len(tasks):
        ready = [t for t in tasks if t["id"] not in done and set(t["deps"]) <= done]
        if not ready:
            raise ValueError("dependency cycle")
        for t in ready:
            out.append(t)
            done.add(t["id"])
    return out


def schedule(tasks: list[dict], durations: dict | None = None, offset: float = 0.0) -> dict:
    """CPM: {id: {"es", "ef", "slack"}}. `durations` overrides expected durations (used for forecasting)."""
    dur = durations or {t["id"]: expected(t) for t in tasks}
    order = _order(tasks)
    es, ef = {}, {}
    for t in order:
        es[t["id"]] = max((ef[d] for d in t["deps"]), default=offset)
        ef[t["id"]] = es[t["id"]] + dur[t["id"]]
    end = max(ef.values())
    ls = {}
    for t in reversed(order):
        succ = [s for s in tasks if t["id"] in s["deps"]]
        lf = min((ls[s["id"]] for s in succ), default=end)
        ls[t["id"]] = lf - dur[t["id"]]
    return {i: {"es": round(es[i], 2), "ef": round(ef[i], 2), "slack": round(ls[i] - es[i], 2)} for i in es}


def critical_path(tasks: list[dict]) -> list[str]:
    s = schedule(tasks)
    return [i for i, v in sorted(s.items(), key=lambda kv: (kv[1]["es"], kv[0])) if abs(v["slack"]) < 1e-9]


def estimate(tasks: list[dict]) -> tuple[float, float]:
    by = {t["id"]: t for t in tasks}
    cp = [by[i] for i in critical_path(tasks)]
    p50 = sum(expected(t) for t in cp)
    sd = math.sqrt(sum(((t["p"] - t["o"]) / 6) ** 2 for t in cp))
    return round(p50, 1), round(p50 + Z90 * sd, 1)


def _replan(eng: dict) -> dict:
    """Schedule the remaining work from `as_of_day`: completed tasks finish "now", the rest are scheduled after."""
    tasks, prog = eng["tasks"], eng.get("progress", {})
    remaining = {t["id"]: expected(t) * (1 - prog.get(t["id"], 0.0)) for t in tasks}
    return schedule(tasks, remaining, offset=eng["as_of_day"])


def forecast(eng: dict) -> dict:
    """Re-plan the remaining work from `as_of_day` using reported progress."""
    tasks = eng["tasks"]
    s = _replan(eng)
    baseline_finish = max(v["ef"] for v in schedule(tasks).values())
    finish = max(v["ef"] for v in s.values())
    return {"baseline_finish_day": round(baseline_finish, 1), "forecast_finish_day": round(finish, 1),
            "slip_days": round(finish - baseline_finish, 1)}


def workstream_rag(eng: dict) -> dict:
    """Earned-value style variance per workstream: (actual - planned progress), weighted by effort."""
    tasks, prog, now = eng["tasks"], eng.get("progress", {}), eng["as_of_day"]
    base = schedule(tasks)
    cp = set(critical_path(tasks))
    out = {}
    for ws in eng["workstreams"]:
        mine = [t for t in tasks if t["workstream"] == ws]
        if not mine:
            continue
        weight = sum(expected(t) for t in mine)
        var, behind_cp = 0.0, False
        for t in mine:
            b = base[t["id"]]
            planned = min(1.0, max(0.0, (now - b["es"]) / (b["ef"] - b["es"])))
            gap = prog.get(t["id"], 0.0) - planned
            var += expected(t) * gap
            behind_cp |= t["id"] in cp and gap < -0.1
        v = var / weight
        rag = "green" if v >= -0.1 else "amber" if v >= -0.25 else "red"
        if behind_cp and rag == "green":
            rag = "amber"
        out[ws] = {"variance": round(v, 3), "rag": rag}
    return out


def next_milestone(eng: dict) -> dict | None:
    """The first unfinished milestone by baseline finish, with its baseline and forecast day and acceptance."""
    base, fc, prog = schedule(eng["tasks"]), _replan(eng), eng.get("progress", {})
    open_ms = [t for t in eng["tasks"] if t.get("milestone") and prog.get(t["id"], 0.0) < 1.0]
    if not open_ms:
        return None
    t = min(open_ms, key=lambda t: (base[t["id"]]["ef"], t["id"]))
    return {"milestone": t["milestone"], "task": t["id"], "acceptance": t.get("acceptance", ""),
            "baseline_day": round(base[t["id"]]["ef"], 1), "forecast_day": round(fc[t["id"]]["ef"], 1)}
