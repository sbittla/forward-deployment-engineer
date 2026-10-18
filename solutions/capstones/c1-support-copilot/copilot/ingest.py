"""Load policy markdown into heading-scoped chunks that keep their section path."""
import re
from dataclasses import dataclass
from pathlib import Path

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


@dataclass(frozen=True)
class Chunk:
    id: str          # "<doc_id>#<section-slug>"
    doc_id: str      # file stem, e.g. "homeowners"
    path: str        # "Homeowners Policy HO-3 > Coverage > Flood"
    text: str        # section body (without the heading line)


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def chunk_markdown(doc_id: str, markdown: str) -> list[Chunk]:
    chunks, trail, body = [], [], []

    def flush():
        text = " ".join(" ".join(body).split())
        if trail and text:
            chunks.append(Chunk(f"{doc_id}#{slug(trail[-1][1])}", doc_id, " > ".join(t[1] for t in trail), text))
        body.clear()

    for line in markdown.splitlines():
        m = HEADING.match(line)
        if m:
            flush()
            level = len(m.group(1))
            trail = [t for t in trail if t[0] < level] + [(level, m.group(2))]
        elif line.strip():
            body.append(line.strip())
    flush()
    return chunks


def load_corpus(policy_dir) -> list[Chunk]:
    out = []
    for p in sorted(Path(policy_dir).glob("*.md")):
        out += chunk_markdown(p.stem, p.read_text(encoding="utf-8"))
    return out
