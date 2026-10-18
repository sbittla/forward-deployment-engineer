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
        for m in messages:
            content = m["content"] if isinstance(m["content"], str) else str(m["content"])
            leaks = phi_scan(content, self.names)
            if leaks:
                raise PHILeak(f"refusing to send prompt containing {', '.join(leaks)}")
        return self.llm.complete(messages, **kw)


def run_pipeline(calls: list[dict], llm) -> list[IntakeResult]:
    results = []
    for call in calls:
        names = [call["patient_name"]]
        raw = caller_transcript(call["events"])
        safe, mapping = deidentify(raw, names)
        intake = extract_intake(_GuardedLLM(llm, names), safe)
        intake, flags = triage(intake, safe)
        results.append(IntakeResult(call["call_id"], intake, flags, call_metrics(call["events"]), len(mapping)))
    return results
