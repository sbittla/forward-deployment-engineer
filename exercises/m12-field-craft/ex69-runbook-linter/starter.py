import re

REQUIRED = ("Overview", "Prerequisites", "Deploy", "Rollback", "Monitoring", "Escalation")


def lint_runbook(markdown: str) -> list[str]:
    raise NotImplementedError
