import inspect


def public_api(module) -> list[str]:
    raise NotImplementedError


def parse_google_docstring(doc: str | None) -> dict:
    raise NotImplementedError


def render_reference(module) -> str:
    raise NotImplementedError


def missing_docs(module) -> list[str]:
    raise NotImplementedError
