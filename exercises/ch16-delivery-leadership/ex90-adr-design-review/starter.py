from dataclasses import dataclass, field

DOWNSIDE_WORDS = {"cost", "risk", "trade-off", "tradeoff", "downside", "slower", "lock-in", "complexity"}
NEGATIONS = {"no", "not", "without", "zero", "nor", "never"}
CHECKLIST = {
    "auth": "blocker", "data_flow": "blocker", "pii_handling": "blocker", "rollback": "blocker",
    "evals": "major", "observability": "major", "threat_model": "major",
    "slo": "minor", "cost_estimate": "minor",
}
RISK_FIELDS = ("risk", "owner", "owner_org", "rationale", "compensating_control", "decided_on", "expires")
MAX_ACCEPTANCE_DAYS = 90


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
    raise NotImplementedError


def lint_adr(adr: ADR) -> list[str]:
    raise NotImplementedError


def review_design(design: dict) -> list[Finding]:
    raise NotImplementedError


def gate(findings: list[Finding], evidence: dict) -> tuple[str, list[str]]:
    raise NotImplementedError


def lint_risk_acceptance(record: dict) -> list[str]:
    raise NotImplementedError
