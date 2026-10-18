REQUIRED = ("name", "version", "owner", "purpose", "users", "out_of_scope", "data_sources", "model_provider",
            "evals", "limitations", "monitoring", "human_oversight")
FLAGS = ("customer_facing", "automated_decision", "regulated_domain")
CONTROLS = {
    3: ["eval suite", "owner sign-off"],
    2: ["monitoring dashboard", "human review of samples"],
    1: ["independent validation", "MRM approval", "kill switch"],
}


def risk_tier(meta: dict) -> int:
    cf, ad, rd = (bool(meta.get(f)) for f in FLAGS)
    if ad and (cf or rd):
        return 1
    return 2 if (cf or ad or rd) else 3


def required_controls(tier: int) -> list[str]:
    out = []
    for t in (3, 2, 1):
        if tier <= t:
            out += CONTROLS[t]
    return out


def validate(meta: dict) -> list[str]:
    issues = [f"missing:{k}" for k in REQUIRED if not meta.get(k)]
    issues += [f"missing:{f}" for f in FLAGS if f not in meta]
    issues += [f"eval_below_threshold:{e['name']}" for e in meta.get("evals", []) if e["value"] < e["threshold"]]
    if risk_tier(meta) == 1:
        oversight = str(meta.get("human_oversight", "")).lower()
        if "review" not in oversight and "approve" not in oversight:
            issues.append("tier1_requires_human_oversight")
    return issues


def _bullets(items) -> list[str]:
    return [f"- {i}" for i in items] or ["- none"]


def render(meta: dict) -> str:
    tier = risk_tier(meta)
    issues = validate(meta)
    lines = [f"# Model risk document: {meta['name']} v{meta['version']}", "",
             "## Summary", f"Owner: {meta.get('owner', '')}", f"Purpose: {meta.get('purpose', '')}",
             f"Model provider: {meta.get('model_provider', '')}", f"Risk tier: {tier}", "",
             "## Intended use", str(meta.get("users", "")), "",
             "## Out of scope", *_bullets(meta.get("out_of_scope", [])), "",
             "## Data", *_bullets(meta.get("data_sources", [])), "",
             "## Evaluation", "| Eval | Metric | Value | Threshold | Status |", "|---|---|---|---|---|"]
    for e in meta.get("evals", []):
        status = "PASS" if e["value"] >= e["threshold"] else "FAIL"
        lines.append(f"| {e['name']} | {e['metric']} | {e['value']} | {e['threshold']} | {status} |")
    lines += ["", "## Limitations", *_bullets(meta.get("limitations", [])), "",
              "## Monitoring", *_bullets(meta.get("monitoring", [])), "",
              "## Human oversight", str(meta.get("human_oversight", "")), "",
              "## Required controls", *_bullets(required_controls(tier)), "",
              "## Approval",
              f"Status: BLOCKED ({len(issues)} issues)" if issues else "Status: READY FOR REVIEW"]
    return "\n".join(lines) + "\n"
