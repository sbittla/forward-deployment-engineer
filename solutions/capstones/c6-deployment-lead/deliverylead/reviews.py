"""Quality bar for partner-built work: design checklist plus evidence gate."""
CHECKLIST = {
    "auth": "blocker", "data_flow": "blocker", "pii_handling": "blocker", "rollback": "blocker",
    "evals": "major", "observability": "major", "threat_model": "major",
    "slo": "minor", "cost_estimate": "minor",
}
ORDER = {"blocker": 0, "major": 1, "minor": 2}


def review_design(design: dict) -> list[tuple[str, str]]:
    findings = [(sev, area) for area, sev in CHECKLIST.items() if not str(design.get(area, "")).strip()]
    pii = str(design.get("pii_handling", "")).lower()
    if "sent to model" in pii and "redact" not in pii:
        findings.append(("blocker", "pii_handling"))
    return sorted(set(findings), key=lambda f: (ORDER[f[0]], f[1]))


def gate(findings: list[tuple[str, str]], evidence: dict) -> tuple[str, list[str]]:
    blockers = sum(s == "blocker" for s, _ in findings)
    majors = sum(s == "major" for s, _ in findings)
    reject, cond = [], []
    if blockers:
        reject.append(f"blocker findings: {blockers}")
    if evidence["open_criticals"]:
        reject.append(f"open critical defects: {evidence['open_criticals']}")
    if majors:
        cond.append(f"major findings: {majors}")
    if evidence["tests_passed"] < evidence["tests_total"]:
        cond.append(f"tests {evidence['tests_passed']}/{evidence['tests_total']}")
    if evidence["eval_pass_rate"] < 0.9:
        cond.append(f"eval pass rate {evidence['eval_pass_rate']} < 0.9")
    if reject:
        return "reject", reject + cond
    return ("conditional", cond) if cond else ("accept", [])


def review_all(deliverables: list[dict]) -> list[dict]:
    out = []
    for d in deliverables:
        findings = review_design(d["design"])
        decision, reasons = gate(findings, d["evidence"])
        out.append({"id": d["id"], "workstream": d["workstream"], "partner": d["partner"], "decision": decision,
                    "reasons": reasons, "findings": findings})
    return out
