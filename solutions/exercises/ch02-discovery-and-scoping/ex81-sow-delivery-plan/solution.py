import math
import re
from dataclasses import dataclass
from datetime import date, timedelta

Z90 = 1.2816
VAGUE_WORDS = {"deployed", "delivered", "done", "complete", "completed", "working", "works", "fast", "faster",
               "better", "good", "improved", "satisfactory", "user-friendly"}


@dataclass(frozen=True)
class Task:
    id: str
    name: str
    optimistic: float
    likely: float
    pessimistic: float
    depends_on: tuple = ()
    owner: str = "fde"
    milestone: str | None = None


@dataclass
class Slot:
    start: float
    finish: float
    slack: float
    critical: bool


def pert(task: Task) -> tuple[float, float]:
    e = (task.optimistic + 4 * task.likely + task.pessimistic) / 6
    return round(e, 2), round((task.pessimistic - task.optimistic) / 6, 2)


def _order(tasks: list[Task]) -> list[Task]:
    ids = {t.id for t in tasks}
    for t in tasks:
        missing = set(t.depends_on) - ids
        if missing:
            raise ValueError(f"{t.id} depends on unknown tasks {sorted(missing)}")
    done, order = set(), []
    while len(order) < len(tasks):
        ready = [t for t in tasks if t.id not in done and set(t.depends_on) <= done]
        if not ready:
            raise ValueError("dependency cycle")
        for t in ready:
            order.append(t)
            done.add(t.id)
    return order


def _expected(t: Task) -> float:
    return (t.optimistic + 4 * t.likely + t.pessimistic) / 6


def schedule(tasks: list[Task]) -> dict[str, Slot]:
    order = _order(tasks)
    es, ef = {}, {}
    for t in order:
        es[t.id] = max((ef[d] for d in t.depends_on), default=0.0)
        ef[t.id] = es[t.id] + _expected(t)
    end = max(ef.values())
    lf, ls = {}, {}
    for t in reversed(order):
        succ = [s for s in tasks if t.id in s.depends_on]
        lf[t.id] = min((ls[s.id] for s in succ), default=end)
        ls[t.id] = lf[t.id] - _expected(t)
    out = {}
    for t in tasks:
        slack = round(ls[t.id] - es[t.id], 2)
        out[t.id] = Slot(round(es[t.id], 2), round(ef[t.id], 2), slack, abs(slack) < 1e-9)
    return out


def critical_path(tasks: list[Task]) -> list[str]:
    s = schedule(tasks)
    return [i for i, _ in sorted(((i, v) for i, v in s.items() if v.critical), key=lambda x: (x[1].start, x[0]))]


def project_estimate(tasks: list[Task]) -> tuple[float, float]:
    by = {t.id: t for t in tasks}
    cp = [by[i] for i in critical_path(tasks)]
    p50 = sum(_expected(t) for t in cp)
    var = sum(((t.pessimistic - t.optimistic) / 6) ** 2 for t in cp)
    return round(p50, 1), round(p50 + Z90 * math.sqrt(var), 1)


def to_dates(day_offset: int, start: date) -> date:
    d = start
    while d.weekday() >= 5:
        d += timedelta(days=1)
    remaining = day_offset
    while remaining > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            remaining -= 1
    return d


def _section(title, items):
    return [f"## {title}"] + [f"- {i}" for i in items] + [""]


def render_sow(engagement: dict, tasks: list[Task], start: date, rate_per_day: float) -> str:
    acc = engagement.get("acceptance", {})
    milestones = [t for t in tasks if t.milestone]
    missing = [t.milestone for t in milestones if t.milestone not in acc]
    if missing:
        raise ValueError(f"milestones without acceptance criteria: {missing}")
    vague = [m for m, text in acc.items() if not re.search(r"\d", text)
             and VAGUE_WORDS & set(re.findall(r"[a-z][a-z-]*", text.lower()))]
    if vague:
        raise ValueError(f"acceptance criteria not measurable: {vague}")
    s = schedule(tasks)
    p50, p90 = project_estimate(tasks)
    lines = ["# Statement of work", ""]
    lines += _section("Objectives", engagement["objectives"])
    lines += _section("In scope", engagement["in_scope"])
    lines += _section("Out of scope", engagement["out_of_scope"])
    lines += ["## Deliverables and acceptance criteria", "| Milestone | Due | Acceptance criteria |", "|---|---|---|"]
    for t in sorted(milestones, key=lambda t: s[t.id].finish):
        due = to_dates(max(0, math.ceil(s[t.id].finish) - 1), start)
        lines.append(f"| {t.milestone} | {due.isoformat()} | {acc[t.milestone]} |")
    lines += ["", "## Timeline", f"Critical path: {' -> '.join(critical_path(tasks))}", ""]
    lines += _section("Assumptions", engagement["assumptions"])
    lines += _section("Customer responsibilities", engagement["customer_responsibilities"])
    lines += ["## Change control",
              "Changes to scope, milestones or acceptance criteria require a written change request approved by "
              "both sponsors; the estimate and timeline are re-baselined on approval.", "",
              "## Estimate",
              f"- P50: {p50} days (${round(p50 * rate_per_day):,})",
              f"- P90: {p90} days (${round(p90 * rate_per_day):,})", ""]
    return "\n".join(lines)
