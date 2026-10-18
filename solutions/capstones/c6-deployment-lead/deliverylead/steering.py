"""Steering-committee update generated from the plan, gates and measurements."""


def render_steering(eng: dict, rag: dict, forecast: dict, reviews: list[dict], security: dict, funnel: dict,
                    impact: dict, decision: dict) -> str:
    week = eng["as_of_day"] // 5 + 1
    overall = {"GO": "GREEN", "GO_WITH_CONDITIONS": "AMBER", "NO_GO": "RED"}[decision["decision"]]
    lines = [f"# {eng['customer']} steering update: week {week}", "",
             "## Overall",
             f"Status: **{overall}**. Go-live readiness: {decision['decision']}. Forecast finish day "
             f"{forecast['forecast_finish_day']} vs baseline {forecast['baseline_finish_day']} "
             f"({forecast['slip_days']:+} days).", "",
             "## Workstreams", "| Workstream | Owner | RAG | Variance |", "|---|---|---|---|"]
    for ws, meta in eng["workstreams"].items():
        if ws in rag:
            lines.append(f"| {ws} | {meta['owner']} | {rag[ws]['rag'].upper()} | {rag[ws]['variance']:+.0%} |")
    lines += ["", "## Partner deliverables", "| Deliverable | Partner | Decision | Reasons |", "|---|---|---|---|"]
    lines += [f"| {r['id']} | {r['partner']} | {r['decision']} | {'; '.join(r['reasons']) or 'none'} |" for r in reviews]
    lines += ["", "## Adoption and impact",
              f"- Activation {funnel['activation_rate']:.0%}, habitual use {funnel['habit_rate']:.0%} of "
              f"{funnel['invited']} invited users.",
              f"- Difference-in-differences effect: {impact['effect']} ({impact['effect_pct']}%) versus the control group.",
              "", "## Security",
              f"- {len(security['answered'])} questions auto-answered from system facts; {len(security['open'])} open "
              "with the security team.",
              "", "## Decisions needed"]
    lines += [f"- {b}" for b in decision["blockers"] + decision["conditions"]] or ["- none"]
    return "\n".join(lines) + "\n"
