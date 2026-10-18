"""Go-live decision: explicit blockers and conditions, never a vibe."""


def go_live(forecast: dict, reviews: list[dict], security: dict, funnel: dict, impact: dict,
            max_slip_days: float = 10, min_activation: float = 0.6, min_effect_pct: float = -10) -> dict:
    blockers, conditions = [], []
    for r in reviews:
        if r["decision"] == "reject":
            blockers.append(f"partner deliverable {r['id']} rejected ({'; '.join(r['reasons'])})")
        elif r["decision"] == "conditional":
            conditions.append(f"partner deliverable {r['id']} accepted with conditions")
    if security["status"] != "clear":
        blockers.append(f"security questionnaire has {len(security['open'])} open items")
    if forecast["slip_days"] > max_slip_days:
        blockers.append(f"forecast slip of {forecast['slip_days']} days exceeds {max_slip_days}")
    if funnel["activation_rate"] < min_activation:
        conditions.append(f"activation {funnel['activation_rate']:.0%} below {min_activation:.0%}")
    if impact["effect_pct"] > min_effect_pct:
        conditions.append(f"measured impact {impact['effect_pct']}% is weaker than the {min_effect_pct}% target")
    decision = "NO_GO" if blockers else "GO_WITH_CONDITIONS" if conditions else "GO"
    return {"decision": decision, "blockers": blockers, "conditions": conditions}
