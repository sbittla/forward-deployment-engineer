import re
from dataclasses import dataclass, field

DOWNSIDE_WORDS = {"cost", "risk", "trade-off", "tradeoff", "downside", "slower", "lock-in", "complexity"}
CHECKLIST = {
    "auth": "blocker", "data_flow": "blocker", "pii_handling": "blocker", "rollback": "blocker",
    "evals": "major", "observability": "major", "threat_model": "major",
    "slo": "minor", "cost_estimate": "minor",
}
REQUIRED = ("context", "decision", "consequences", "alternatives considered")
SEVERITY_ORDER = {"blocker": 0, "major": 1, "minor": 2}


@dataclass
class ADR:
    number: int
    title: str
    status: str
    sections: dict = field(default_factory=dict)


@dataclass
class Finding:
    severity: str
    area: str
    message: str


def parse_adr(markdown: str) -> ADR:
    lines = markdown.strip().splitlines()
    m = re.match(r"^#\s+ADR-(\d+):\s*(.+)$", lines[0]) if lines else None
    if not m:
        raise ValueError("first line must be '# ADR-<n>: <title>'")
    st = re.search(r"^status:\s*(proposed|accepted|superseded|rejected)\s*$", markdown, re.I | re.M)
    if not st:
        raise ValueError("missing or invalid Status line")
    sections = {}
    for chunk in re.split(r"^##\s+", markdown, flags=re.M)[1:]:
        head, _, body = chunk.partition("\n")
        sections[head.strip().lower()] = body.strip()
    return ADR(int(m.group(1)), m.group(2).strip(), st.group(1).lower(), sections)


def lint_adr(adr: ADR) -> list[str]:
    issues = [f"missing:{s}" for s in REQUIRED if s not in adr.sections]
    alts = adr.sections.get("alternatives considered")
    if alts is not None and len(re.findall(r"^\s*[-*]\s+", alts, re.M)) < 2:
        issues.append("alternatives:fewer-than-2")
    cons = adr.sections.get("consequences")
    if cons is not None and not any(w in cons.lower() for w in DOWNSIDE_WORDS):
        issues.append("consequences:no-downside")
    if adr.status == "accepted" and "decided-by:" not in adr.sections.get("decision", "").lower():
        issues.append("decision:no-owner")
    return issues


def review_design(design: dict) -> list[Finding]:
    findings = [Finding(sev, area, f"{area} is missing from the design") for area, sev in CHECKLIST.items()
                if not str(design.get(area, "")).strip()]
    pii = str(design.get("pii_handling", "")).lower()
    if "sent to model" in pii and "redact" not in pii:
        findings.append(Finding("blocker", "pii_handling", "PII reaches the model without redaction"))
    return sorted(findings, key=lambda f: (SEVERITY_ORDER[f.severity], f.area))


def gate(findings: list[Finding], evidence: dict) -> tuple[str, list[str]]:
    blockers = sum(f.severity == "blocker" for f in findings)
    majors = sum(f.severity == "major" for f in findings)
    reject, conditional = [], []
    if blockers:
        reject.append(f"blocker findings: {blockers}")
    if evidence["open_criticals"] > 0:
        reject.append(f"open critical defects: {evidence['open_criticals']}")
    if majors:
        conditional.append(f"major findings: {majors}")
    if evidence["tests_passed"] < evidence["tests_total"]:
        conditional.append(f"tests {evidence['tests_passed']}/{evidence['tests_total']}")
    if evidence["eval_pass_rate"] < 0.9:
        conditional.append(f"eval pass rate {evidence['eval_pass_rate']} < 0.9")
    if reject:
        return "reject", reject + conditional
    if conditional:
        return "conditional", conditional
    return "accept", []
