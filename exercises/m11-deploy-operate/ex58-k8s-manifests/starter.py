import yaml


def load(path) -> list[dict]:
    raise NotImplementedError


def lint_manifests(docs: list[dict]) -> list[str]:
    raise NotImplementedError
