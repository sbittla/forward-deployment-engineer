from dataclasses import dataclass, field


class ScopeError(Exception):
    pass


@dataclass(frozen=True)
class Feature:
    name: str
    priority: str
    value: float
    effort: float
    depends_on: tuple[str, ...] = ()


@dataclass
class Plan:
    included: list[str] = field(default_factory=list)
    deferred: list[str] = field(default_factory=list)
    slack: float = 0


def _closure(f, by_name, included, seen=None):
    """Features (deps first) needed to ship f; None if a dep is 'wont' or unknown."""
    seen = seen or set()
    order = []
    for d in f.depends_on:
        if d in included or d in seen:
            continue
        dep = by_name.get(d)
        if dep is None or dep.priority == "wont":
            return None
        sub = _closure(dep, by_name, included, seen | {f.name})
        if sub is None:
            return None
        order += [x for x in sub if x not in order]
    return order + [f]


def _fmt(x):
    return int(x) if float(x).is_integer() else x


def plan(features: list[Feature], capacity: float) -> Plan:
    by_name = {f.name: f for f in features}
    included: list[str] = []
    used = 0.0

    musts = [f for f in features if f.priority == "must"]
    for f in musts:
        for x in _closure(f, by_name, set(included)) or [f]:
            if x.name not in included:
                included.append(x.name)
                used += x.effort
    if used > capacity:
        raise ScopeError(f"musts need {_fmt(used)} days, capacity {_fmt(capacity)}")

    for tier in ("should", "could"):
        cands = sorted((f for f in features if f.priority == tier),
                       key=lambda f: (-f.value / f.effort, f.name))
        for f in cands:
            if f.name in included:
                continue
            chain = _closure(f, by_name, set(included))
            if chain is None:
                continue
            cost = sum(x.effort for x in chain)
            if used + cost <= capacity:
                for x in chain:
                    included.append(x.name)
                used += cost

    deferred = sorted(f.name for f in features if f.name not in included)
    return Plan(included=included, deferred=deferred, slack=_fmt(capacity - used))


def tradeoff_message(p: Plan) -> str:
    deferred = ", ".join(p.deferred) if p.deferred else "none"
    return f"Included: {', '.join(p.included)}. Deferred to phase 2: {deferred}. Slack: {_fmt(p.slack)} days."
