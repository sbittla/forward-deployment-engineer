import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Entity:
    type: str
    start: int
    end: int
    value: str


PATTERNS = [
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("SSN", re.compile(r"\b(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b")),
    ("CREDIT_CARD", re.compile(r"\b\d(?:[ -]?\d){12,18}\b")),
    ("PHONE", re.compile(r"(?<![\w-])(?:\+?1[ .-]?)?(?:\(\d{3}\)\s?|\d{3}[ .-])\d{3}[ .-]\d{4}\b")),
    ("IP", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
]


def luhn_ok(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d = d * 2 - 9 if d > 4 else d * 2
        total += d
    return total % 10 == 0


def detect(text: str) -> list[Entity]:
    found = []
    for typ, rx in PATTERNS:
        for m in rx.finditer(text):
            if typ == "CREDIT_CARD":
                digits = re.sub(r"\D", "", m.group(0))
                if not 13 <= len(digits) <= 19 or not luhn_ok(digits):
                    continue
            found.append(Entity(typ, m.start(), m.end(), m.group(0)))
    found.sort(key=lambda e: (e.start, -(e.end - e.start)))
    out, last_end = [], -1
    for e in found:
        if e.start >= last_end:
            out.append(e)
            last_end = e.end
    return out


def redact(text: str, mode: str = "token") -> tuple[str, dict[str, str]]:
    mapping: dict[str, str] = {}
    by_value: dict[tuple[str, str], str] = {}
    counters: dict[str, int] = {}
    parts, pos = [], 0
    for e in detect(text):
        parts.append(text[pos:e.start])
        if mode == "mask":
            parts.append(f"[{e.type}]")
        else:
            key = (e.type, e.value)
            if key not in by_value:
                counters[e.type] = counters.get(e.type, 0) + 1
                token = f"[{e.type}_{counters[e.type]}]"
                by_value[key] = token
                mapping[token] = e.value
            parts.append(by_value[key])
        pos = e.end
    parts.append(text[pos:])
    return "".join(parts), mapping


def restore(text: str, mapping: dict[str, str]) -> str:
    for token, value in mapping.items():
        text = text.replace(token, value)
    return text
