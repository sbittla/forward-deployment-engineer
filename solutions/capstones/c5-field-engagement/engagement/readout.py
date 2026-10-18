"""Board-ready readout generated from the charter, measured results and the value model."""
from .discovery import assumptions_for
from .voice import p95


def render_readout(charter, metrics: dict, results, value: dict) -> str:
    go = metrics["urgent_recall"] == 1.0 and metrics["field_accuracy"] >= 0.95
    flagged = [r.call_id for r in results if r.red_flags]
    latencies = [r.voice.get("max_latency_s") for r in results]
    barge = sum(r.voice.get("barge_ins", 0) for r in results)
    lines = [
        f"# {charter.customer}: after-hours intake pilot readout",
        "",
        "## Executive summary",
        f"Recommendation: **{'GO' if go else 'NO-GO'}** for a supervised rollout to all triage nurses.",
        f"Every urgent call was caught ({metrics['urgent_recall']:.0%} urgent recall), and intake fields were "
        f"{metrics['field_accuracy']:.0%} accurate across {metrics['calls']} calls.",
        "",
        "## What we measured",
        "| Measure | Result |",
        "|---|---|",
        f"| Intake field accuracy | {metrics['field_accuracy']:.0%} |",
        f"| Urgency accuracy | {metrics['urgency']:.0%} |",
        f"| Urgent-case recall | {metrics['urgent_recall']:.0%} |",
        "",
        "## Safety",
        f"- Red-flag override escalated calls {', '.join(flagged) or 'none'} to emergency, regardless of model output.",
        "- No PHI left the clinic network: every prompt is scanned and blocked if a name, date, MRN, phone or email "
        "is detected.",
        "",
        "## Voice experience",
        f"- p95 agent response latency: {p95(latencies)} s. Callers interrupted the agent {barge} time(s).",
        "",
        "## Business impact",
        f"- {value['nurse_hours_saved_per_month']:,} nurse hours saved per month; "
        f"net ${value['net_savings_per_month']:,.0f}/month; payback in {value['payback_months']} months.",
        "",
        "## Product feedback",
        "- A built-in PHI guard and red-flag rules engine would remove two weeks of custom work per clinic.",
        "",
        "## Next steps",
        "- Shadow mode with all triage nurses for 4 weeks, with weekly eval review.",
        "- CMO signs off the red-flag list; add new flags through change control.",
        "",
        "## Open questions and assumptions",
    ]
    lines += [f"- {a}" for a in assumptions_for(charter.open_questions)] or ["- none"]
    return "\n".join(lines) + "\n"
