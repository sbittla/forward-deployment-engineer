from dataclasses import dataclass, field


@dataclass
class Stakeholder:
    name: str
    role: str
    influence: int
    interest: int
    raci: dict[str, str] = field(default_factory=dict)


CADENCE = {
    "manage closely": ("weekly", "1:1"),
    "keep satisfied": ("biweekly", "exec summary"),
    "keep informed": ("weekly", "status email"),
    "monitor": ("monthly", "newsletter"),
}


def quadrant(s: Stakeholder) -> str:
    if s.influence >= 4 and s.interest >= 4:
        return "manage closely"
    if s.influence >= 4:
        return "keep satisfied"
    if s.interest >= 4:
        return "keep informed"
    return "monitor"


def validate_raci(stakeholders: list[Stakeholder], workstreams: list[str]) -> list[str]:
    issues = []
    for s in stakeholders:
        for ws, letter in s.raci.items():
            if ws not in workstreams:
                issues.append(f"{s.name} has a RACI entry for unknown workstream '{ws}'")
            if letter not in "RACI" or len(letter) != 1:
                issues.append(f"{s.name} has invalid RACI letter '{letter}' for '{ws}'")
    for ws in workstreams:
        letters = [s.raci.get(ws) for s in stakeholders]
        a, r = letters.count("A"), letters.count("R")
        if a != 1:
            issues.append(f"workstream '{ws}' needs exactly one A (has {a})")
        if r < 1:
            issues.append(f"workstream '{ws}' has no R (responsible)")
    return issues


def comms_plan(stakeholders: list[Stakeholder]) -> list[tuple[str, str, str, str]]:
    rows = []
    for s in sorted(stakeholders, key=lambda s: (-s.influence, s.name)):
        q = quadrant(s)
        rows.append((s.name, q, *CADENCE[q]))
    return rows
