"""The POC pipeline running inside the clinic tenant: transcript -> de-identify -> guard -> extract -> triage."""
from dataclasses import dataclass, field

from .deid import PHILeak, deidentify, phi_scan
from .intake import extract_intake, triage
from .voice import call_metrics, caller_transcript


@dataclass
class IntakeResult:
    call_id: str
    intake: dict
    red_flags: list[str] = field(default_factory=list)
    voice: dict = field(default_factory=dict)
    phi_tokens: int = 0


class _GuardedLLM:
    """Every prompt is scanned for PHI immediately before it would leave the network."""

    def __init__(self, llm, names):
        self.llm, self.names = llm, names

    def complete(self, messages, **kw):
        raise NotImplementedError


def run_pipeline(calls: list[dict], llm) -> list[IntakeResult]:
    raise NotImplementedError
