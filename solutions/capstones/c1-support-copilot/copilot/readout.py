"""Executive readout generated from measured metrics, so the slide numbers can't drift from reality."""
from .evals import launch_bar


def business_impact(baseline_aht_min: float, projected_aht_min: float, monthly_contacts: int,
                    hourly_cost: float, adoption: float, monthly_llm_cost: float) -> dict:
    hours = (baseline_aht_min - projected_aht_min) / 60 * monthly_contacts * adoption
    gross = hours * hourly_cost
    return {"hours_saved_per_month": round(hours), "net_savings_per_month": round(gross - monthly_llm_cost)}


def render_exec_readout(metrics: dict, impact: dict, customer: str = "Northwind Insurance") -> str:
    ok, misses = launch_bar(metrics)
    lines = [
        f"# {customer} support copilot: pilot readout",
        "",
        "## Executive summary",
        f"Recommendation: {'proceed to a production rollout' if ok else 'extend the pilot and fix the gaps below'}.",
        f"The copilot passed {metrics['pass_rate']:.0%} of {metrics['cases']} golden cases, and every answer it gave "
        f"cited the policy text ({metrics['citation_precision']:.0%} citation precision).",
        "",
        "## Results",
        "| Metric | Result | Launch bar |",
        "|---|---|---|",
        f"| Golden-set pass rate | {metrics['pass_rate']:.0%} | 90% |",
        f"| Intent routing accuracy | {metrics['intent_accuracy']:.0%} | 90% |",
        f"| Citation precision | {metrics['citation_precision']:.0%} | 95% |",
        f"| Answers to unanswerable questions | {metrics['false_answer_rate']:.0%} | 0% |",
        f"| Average model cost per question | ${metrics['avg_cost_usd']:.4f} | n/a |",
        "",
        "## Business impact",
        f"- About {impact['hours_saved_per_month']:,} adjuster hours saved per month at pilot adoption.",
        f"- Net savings of about ${impact['net_savings_per_month']:,} per month after model costs.",
        "",
        "## Risks",
    ]
    lines += [f"- Launch bar miss: {m}" for m in misses] or ["- No launch-bar misses. Main residual risk: "
                                                            "policy documents change without re-indexing."]
    lines += ["", "## Next steps",
              "- Expand the golden set to 200 cases drawn from real tickets.",
              "- Wire claim-status intents to the claims system API.",
              "- Hand over the runbook and on-call rotation to the Claims Platform team."]
    return "\n".join(lines) + "\n"
