"""Tokenise PII before anything leaves the customer's boundary; restore it in the final answer."""
import re

PATTERNS = [
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
    ("POLICY", re.compile(r"\bPOL-\d{6}\b")),
    ("PHONE", re.compile(r"(?<!\w)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b")),
]
TOKEN = re.compile(r"\[(?:EMAIL|POLICY|PHONE)_\d+\]")


def redact(text: str) -> tuple[str, dict[str, str]]:
    raise NotImplementedError


def restore(text: str, mapping: dict[str, str]) -> str:
    raise NotImplementedError


def strip_tokens(text: str) -> str:
    """Remove PII tokens so they don't pollute retrieval."""
    raise NotImplementedError
