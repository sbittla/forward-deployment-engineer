import re
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
    stakeholders: list[tuple[str, str]] = field(default_factory=list)
    metrics: list[Metric] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)


METRIC_RE = re.compile(r"^(?P<name>[^:]+):\s*(?P<base>[\d.]+)\s*\S*\s*->\s*(?P<target>[\d.]+)\s*(?P<unit>.*)$")


def _bullets(body: str) -> list[str]:
    return [ln.strip()[2:].strip() for ln in body.splitlines() if ln.strip().startswith("- ")]


def _num(s: str) -> float:
    v = float(s)
    return int(v) if v.is_integer() else v


def parse_notes(text: str) -> Charter:
    c = Charter()
    for chunk in re.split(r"^## ", text, flags=re.M)[1:]:
        title, _, body = chunk.partition("\n")
        key = title.strip().lower()
        if key == "customer":
            c.customer = body.strip()
        elif key == "problem":
            c.problem = " ".join(body.split())
        elif key == "stakeholders":
            for b in _bullets(body):
                parts = re.split(r"\s+[—-]\s+", b, maxsplit=1)
                role = parts[1] if len(parts) > 1 else ""
                c.stakeholders.append((parts[0].strip(), role.strip()))
        elif key == "success metrics":
            for b in _bullets(body):
                m = METRIC_RE.match(b)
                if m:
                    c.metrics.append(Metric(m["name"].strip(), _num(m["base"]), _num(m["target"]), m["unit"].strip()))
                else:
                    c.metrics.append(Metric(b, None, None))
        elif key == "constraints":
            c.constraints = _bullets(body)
        elif key == "out of scope":
            c.out_of_scope = _bullets(body)
    return c


def validate(charter: Charter) -> list[str]:
    issues = []
    if not charter.problem.strip():
        issues.append("missing problem statement")
    if not any("sponsor" in role.lower() for _, role in charter.stakeholders):
        issues.append("no executive sponsor identified")
    for m in charter.metrics:
        if m.baseline is None or m.target is None:
            issues.append(f"metric '{m.name}' is not measurable (needs numeric baseline and target)")
    if not charter.out_of_scope:
        issues.append("out-of-scope list is empty")
    return issues


def render(charter: Charter) -> str:
    lines = [f"# Engagement charter: {charter.customer}", "", "## Problem", charter.problem, "", "## Stakeholders"]
    lines += [f"- {n} — {r}" for n, r in charter.stakeholders]
    lines += ["", "## Success metrics", "| Metric | Baseline | Target | Unit |", "|---|---|---|---|"]
    for m in charter.metrics:
        b = "?" if m.baseline is None else m.baseline
        t = "?" if m.target is None else m.target
        lines.append(f"| {m.name} | {b} | {t} | {m.unit} |")
    lines += ["", "## Constraints"] + [f"- {x}" for x in charter.constraints]
    lines += ["", "## Out of scope"] + [f"- {x}" for x in charter.out_of_scope]
    return "\n".join(lines) + "\n"
