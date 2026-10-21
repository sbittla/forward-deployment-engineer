def lint_policy(policy: dict) -> list[str]:
    raise NotImplementedError


def generate_policy(needs: list[tuple[str, str]]) -> dict:
    raise NotImplementedError


def lint_terraform(doc: dict) -> list[str]:
    raise NotImplementedError
