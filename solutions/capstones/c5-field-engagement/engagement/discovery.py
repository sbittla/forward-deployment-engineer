"""Discovery artefacts: charter from on-site notes, explicit assumptions, and a time-boxed engagement plan."""
import re
from dataclasses import dataclass, field
from datetime import date, timedelta

METRIC = re.compile(r"^(?P<name>[^:]+):\s*(?P<base>[\d.]+)\s*\S*\s*->\s*(?P<target>[\d.]+)\s*(?P<unit>.*)$")

DEFAULT_ASSUMPTIONS = {
    "owns": "the CMO owns the red-flag list; the Nurse Manager proposes changes",
    "retention": "transcripts are kept 30 days and recordings are not copied out of the clinic tenant",
    "batch": "calls are processed within 5 minutes of hang-up (near-real-time), not overnight",
}


@dataclass
class Charter:
    customer: str = ""
    problem: str = ""
    stakeholders: list[tuple[str, str]] = field(default_factory=list)
    metrics: list[dict] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)


def _bullets(body):
    return [l.strip()[2:].strip() for l in body.splitlines() if l.strip().startswith("- ")]


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
                c.stakeholders.append((parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""))
        elif key == "success metrics":
            for b in _bullets(body):
                m = METRIC.match(b)
                c.metrics.append({"name": m["name"].strip(), "baseline": float(m["base"]),
                                  "target": float(m["target"]), "unit": m["unit"].strip()} if m else
                                 {"name": b, "baseline": None, "target": None, "unit": ""})
        elif key == "constraints":
            c.constraints = _bullets(body)
        elif key == "out of scope":
            c.out_of_scope = _bullets(body)
        elif key == "open questions":
            c.open_questions = _bullets(body)
    return c


def validate_charter(c: Charter) -> list[str]:
    issues = []
    if not any("sponsor" in r.lower() for _, r in c.stakeholders):
        issues.append("no executive sponsor")
    issues += [f"metric '{m['name']}' is not measurable" for m in c.metrics if m["baseline"] is None]
    if not c.out_of_scope:
        issues.append("out-of-scope list is empty")
    return issues


def assumptions_for(open_questions: list[str]) -> list[str]:
    out = []
    for q in open_questions:
        default = next((v for k, v in DEFAULT_ASSUMPTIONS.items() if k in q.lower()),
                       "we take the most conservative option and confirm with the sponsor")
        out.append(f"{q} -> Until confirmed, we assume {default}.")
    return out


MILESTONES = [
    "Discovery complete and charter signed",
    "POC demo on de-identified real calls",
    "Eval set and red-flag list signed off",
    "Pipeline running inside the clinic tenant",
    "Shadow pilot with two triage nurses",
    "Executive readout and go/no-go",
]


def engagement_plan(start: date, weeks: int = 6) -> list[tuple[int, date, str]]:
    """One milestone per week, due on that week's Friday."""
    first_friday = start + timedelta(days=(4 - start.weekday()) % 7)
    return [(w, first_friday + timedelta(weeks=w - 1), MILESTONES[w - 1]) for w in range(1, weeks + 1)]
