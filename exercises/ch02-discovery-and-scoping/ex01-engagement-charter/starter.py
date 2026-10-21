from dataclasses import dataclass, field


@dataclass
class Metric:
    name: str
    baseline: float | None
    target: float | None
    unit: str = ""


@dataclass
class Charter:
    customer: str = ""
    problem: str = ""
    stakeholders: list[tuple[str, str]] = field(default_factory=list)  # (name, role)
    metrics: list[Metric] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)


def parse_notes(text: str) -> Charter:
    raise NotImplementedError


def validate(charter: Charter) -> list[str]:
    raise NotImplementedError


def render(charter: Charter) -> str:
    raise NotImplementedError
