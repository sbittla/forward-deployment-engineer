"""Tokenise PII before anything leaves the customer's boundary; restore it in the final answer."""
import re

PATTERNS = [
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
    ("POLICY", re.compile(r"\bPOL-\d{6}\b")),
    ("PHONE", re.compile(r"(?<!\w)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b")),
]
TOKEN = re.compile(r"\[(?:EMAIL|POLICY|PHONE)_\d+\]")


def redact(text: str) -> tuple[str, dict[str, str]]:
    mapping: dict[str, str] = {}
    seen: dict[str, str] = {}
    counters: dict[str, int] = {}
    for kind, rx in PATTERNS:
        def sub(m, kind=kind):
            value = m.group(0)
            if value not in seen:
                counters[kind] = counters.get(kind, 0) + 1
                seen[value] = f"[{kind}_{counters[kind]}]"
                mapping[seen[value]] = value
            return seen[value]
        text = rx.sub(sub, text)
    return text, mapping


def restore(text: str, mapping: dict[str, str]) -> str:
    for token, value in mapping.items():
        text = text.replace(token, value)
    return text


def strip_tokens(text: str) -> str:
    """Remove PII tokens so they don't pollute retrieval."""
    return TOKEN.sub(" ", text)
