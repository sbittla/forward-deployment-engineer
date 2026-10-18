"""PHI de-identification and a hard guard that nothing identifiable leaves the clinic network."""
import re

PATTERNS = [
    ("MRN", re.compile(r"\bMRN[:#\s]*\d+\b", re.I)),
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
    ("DATE", re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b")),
    ("PHONE", re.compile(r"(?<!\w)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b")),
]


class PHILeak(Exception):
    pass


def deidentify(text: str, names: list[str]) -> tuple[str, dict[str, str]]:
    raise NotImplementedError


def phi_scan(text: str, names: list[str]) -> list[str]:
    """Return the kinds of PHI still present (empty list = safe to send)."""
    raise NotImplementedError
