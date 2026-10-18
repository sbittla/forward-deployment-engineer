"""Quality bar for partner-built work: design checklist plus evidence gate."""
CHECKLIST = {
    "auth": "blocker", "data_flow": "blocker", "pii_handling": "blocker", "rollback": "blocker",
    "evals": "major", "observability": "major", "threat_model": "major",
    "slo": "minor", "cost_estimate": "minor",
}
ORDER = {"blocker": 0, "major": 1, "minor": 2}


def review_design(design: dict) -> list[tuple[str, str]]:
    raise NotImplementedError


def gate(findings: list[tuple[str, str]], evidence: dict) -> tuple[str, list[str]]:
    raise NotImplementedError


def review_all(deliverables: list[dict]) -> list[dict]:
    raise NotImplementedError
