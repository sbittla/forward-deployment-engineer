"""The customer platform team's admission policy, as code (subset of ex57-ex59)."""
import re

SECRET_NAME = re.compile(r"KEY|SECRET|TOKEN|PASSWORD", re.I)


def _tag_ok(image: str) -> bool:
    raise NotImplementedError


def lint_dockerfile(text: str) -> list[str]:
    raise NotImplementedError


def lint_k8s(docs: list[dict]) -> list[str]:
    raise NotImplementedError


def lint_ci(doc: dict) -> list[str]:
    raise NotImplementedError
