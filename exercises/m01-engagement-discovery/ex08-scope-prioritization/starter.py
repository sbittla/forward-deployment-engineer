from dataclasses import dataclass, field


class ScopeError(Exception):
    pass


@dataclass(frozen=True)
class Feature:
    name: str
    priority: str  # must | should | could | wont
    value: float
    effort: float
    depends_on: tuple[str, ...] = ()


@dataclass
class Plan:
    included: list[str] = field(default_factory=list)
    deferred: list[str] = field(default_factory=list)
    slack: float = 0


def plan(features: list[Feature], capacity: float) -> Plan:
    raise NotImplementedError


def tradeoff_message(p: Plan) -> str:
    raise NotImplementedError
