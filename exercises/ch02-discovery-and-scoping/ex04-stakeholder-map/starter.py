from dataclasses import dataclass, field


@dataclass
class Stakeholder:
    name: str
    role: str
    influence: int
    interest: int
    raci: dict[str, str] = field(default_factory=dict)


def quadrant(s: Stakeholder) -> str:
    raise NotImplementedError


def validate_raci(stakeholders: list[Stakeholder], workstreams: list[str]) -> list[str]:
    raise NotImplementedError


def comms_plan(stakeholders: list[Stakeholder]) -> list[tuple[str, str, str, str]]:
    raise NotImplementedError
