import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Chunk:
    text: str
    start: int
    end: int
    meta: dict = field(default_factory=dict)


def fixed_chunks(text: str, size: int, overlap: int) -> list[Chunk]:
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    step, out = size - overlap, []
    for start in range(0, len(text), step):
        end = min(start + size, len(text))
        out.append(Chunk(text[start:end], start, end))
        if end == len(text):
            break
    return out


def _split_keep(text: str, sep: str) -> list[str]:
    parts = text.split(sep)
    return [p + sep for p in parts[:-1]] + ([parts[-1]] if parts[-1] else [])


def _recurse(text: str, max_chars: int, seps: tuple) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    sep = next((s for s in seps if s in text), None)
    if sep is None:
        return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
    rest = seps[seps.index(sep) + 1:]
    pieces = []
    for p in _split_keep(text, sep):
        pieces += _recurse(p, max_chars, rest) if len(p) > max_chars else [p]
    merged, cur = [], ""
    for p in pieces:
        if cur and len(cur) + len(p) > max_chars:
            merged.append(cur)
            cur = ""
        cur += p
    if cur:
        merged.append(cur)
    return merged


def recursive_chunks(text: str, max_chars: int, separators=("\n\n", "\n", ". ", " ")) -> list[Chunk]:
    out, pos = [], 0
    for piece in _recurse(text, max_chars, tuple(separators)):
        out.append(Chunk(piece, pos, pos + len(piece)))
        pos += len(piece)
    return out


HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)


def heading_chunks(markdown: str) -> list[Chunk]:
    marks = list(HEADING.finditer(markdown))
    bounds = [0] + [m.start() for m in marks] + [len(markdown)]
    trail: list[tuple[int, str]] = []
    out = []
    if marks and marks[0].start() > 0 or not marks:
        out.append(Chunk(markdown[: bounds[1]], 0, bounds[1], {"path": ""}))
    for i, m in enumerate(marks):
        level = len(m.group(1))
        trail = [t for t in trail if t[0] < level] + [(level, m.group(2))]
        start, end = m.start(), bounds[i + 2]
        out.append(Chunk(markdown[start:end], start, end, {"path": " > ".join(t[1] for t in trail)}))
    return out


def chunk_key(doc_id: str, path: str, text: str) -> str:
    return hashlib.sha256(json.dumps([doc_id, path, text]).encode()).hexdigest()


def plan_reindex(doc_id: str, current: dict[str, str], incoming: list[Chunk]) -> tuple[list[Chunk], list[str]]:
    fresh = {chunk_key(doc_id, c.meta.get("path", ""), c.text): c for c in incoming}
    to_add = [chunk for key, chunk in fresh.items() if key not in current]
    to_delete = [idx for key, idx in current.items() if key not in fresh]
    return to_add, to_delete


def _as_date(value) -> date | None:
    if value is None or isinstance(value, date):
        return value
    return date.fromisoformat(value)


def filter_effective(chunks: list[Chunk], on: date) -> list[Chunk]:
    out = []
    for c in chunks:
        start, end = _as_date(c.meta.get("effective_from")), _as_date(c.meta.get("effective_to"))
        if (start is None or start <= on) and (end is None or on < end):
            out.append(c)
    return out
