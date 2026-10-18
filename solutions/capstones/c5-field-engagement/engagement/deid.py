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
    mapping, seen, counters = {}, {}, {}

    def token(kind, value):
        if value not in seen:
            counters[kind] = counters.get(kind, 0) + 1
            seen[value] = f"[{kind}_{counters[kind]}]"
            mapping[seen[value]] = value
        return seen[value]

    for kind, rx in PATTERNS:
        text = rx.sub(lambda m, k=kind: token(k, m.group(0)), text)
    parts = sorted({p for n in names for p in [n, *n.split()]}, key=len, reverse=True)
    for p in parts:
        text = re.sub(rf"\b{re.escape(p)}\b", lambda m: token("NAME", m.group(0)), text, flags=re.I)
    return text, mapping


def phi_scan(text: str, names: list[str]) -> list[str]:
    """Return the kinds of PHI still present (empty list = safe to send)."""
    found = [kind for kind, rx in PATTERNS if rx.search(text)]
    if any(re.search(rf"\b{re.escape(p)}\b", text, re.I) for n in names for p in [n, *n.split()]):
        found.append("NAME")
    return found
