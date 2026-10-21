"""Steering-committee update generated from the plan, gates and measurements, with the decision first."""
from .plan import forecast as _forecast
from .plan import next_milestone, workstream_rag


def _changes(eng: dict, rag: dict, fc: dict) -> list[str]:
    last = eng.get("last_week")
    if not last:
        return ["- No previous snapshot to compare with."]
    before = {**eng, **last}
    prev_prog, prog = last.get("progress", {}), eng.get("progress", {})
    delivered = [t["id"] for t in eng["tasks"] if prog.get(t["id"], 0.0) >= 1.0 > prev_prog.get(t["id"], 0.0)]
    order = {"green": 0, "amber": 1, "red": 2}
    prev_rag = workstream_rag(before)
    worse = [f"{ws} {prev_rag[ws]['rag'].upper()} -> {r['rag'].upper()}" for ws, r in rag.items()
             if ws in prev_rag and order[r["rag"]] > order[prev_rag[ws]["rag"]]]
    prev_finish = _forecast(before)["forecast_finish_day"]
    moved = round(fc["forecast_finish_day"] - prev_finish, 1)
    return [f"- Delivered: {', '.join(delivered) or 'none'}.",
            f"- Slipped or newly at risk: {'; '.join(worse) or 'none'}.",
            f"- Forecast finish: day {fc['forecast_finish_day']}, was day {prev_finish} last week ({moved:+} days)."]


def _risks(eng: dict, security: dict) -> list[str]:
    items = sorted((r for r in eng.get("raid", []) if r.get("status", "open") == "open"),
                   key=lambda r: (r.get("due") or "9999-99-99", r["id"]))
    lines = [f"- {r['id']} {r['type']}: {r['text']} (owner: {r.get('owner') or 'UNASSIGNED'}, "
             f"due {r.get('due') or 'NO DATE'})" for r in items]
    lines.append(f"- Security: {len(security['answered'])} questions auto-answered from system facts; "
                 f"{len(security['open'])} open with the security team.")
    return lines


def render_steering(eng: dict, rag: dict, forecast: dict, reviews: list[dict], security: dict, funnel: dict,
                    impact: dict, decision: dict) -> str:
    week = eng["as_of_day"] // 5 + 1
    overall = {"GO": "GREEN", "GO_WITH_CONDITIONS": "AMBER", "NO_GO": "RED"}[decision["decision"]]
    lines = [f"# {eng['customer']} steering update: week {week}", "", "## Decisions needed"]
    lines += [f"- {b}" for b in decision["blockers"] + decision["conditions"]] or ["- none"]
    lines += ["", "## Overall",
              f"Status: **{overall}**. Go-live readiness: {decision['decision']}. Forecast finish day "
              f"{forecast['forecast_finish_day']} vs baseline {forecast['baseline_finish_day']} "
              f"({forecast['slip_days']:+} days).", "", "## Changed since last week"]
    lines += _changes(eng, rag, forecast)
    lines += ["", "### Workstreams", "| Workstream | Owner | RAG | Variance |", "|---|---|---|---|"]
    for ws, meta in eng["workstreams"].items():
        if ws in rag:
            lines.append(f"| {ws} | {meta['owner']} | {rag[ws]['rag'].upper()} | {rag[ws]['variance']:+.0%} |")
    lines += ["", "### Partner deliverables", "| Deliverable | Partner | Decision | Reasons |", "|---|---|---|---|"]
    lines += [f"| {r['id']} | {r['partner']} | {r['decision']} | {'; '.join(r['reasons']) or 'none'} |" for r in reviews]
    lines += ["", "## Adoption and impact",
              f"- Activation {funnel['activation_rate']:.0%}, habitual use {funnel['habit_rate']:.0%} of "
              f"{funnel['invited']} invited users.",
              f"- Difference-in-differences effect: {impact['effect']} ({impact['effect_pct']}%) versus the control group.",
              "", "## Risks and asks"]
    lines += _risks(eng, security)
    lines += ["", "## Next milestone"]
    ms = next_milestone(eng)
    lines.append(f"- {ms['milestone']} ({ms['task']}): forecast day {ms['forecast_day']} vs baseline "
                 f"{ms['baseline_day']}. Acceptance: {ms['acceptance'] or 'NOT DEFINED'}." if ms else "- none")
    return "\n".join(lines) + "\n"
