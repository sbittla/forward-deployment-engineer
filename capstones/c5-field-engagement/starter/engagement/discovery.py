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
    raise NotImplementedError


def parse_notes(text: str) -> Charter:
    raise NotImplementedError


def validate_charter(c: Charter) -> list[str]:
    raise NotImplementedError


def assumptions_for(open_questions: list[str]) -> list[str]:
    raise NotImplementedError


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
    raise NotImplementedError
