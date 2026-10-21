"""Load policy markdown into heading-scoped chunks that keep their section path; sync changes incrementally."""
import hashlib
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


def sync_corpus(policy_dir, previous: dict | None = None) -> tuple[dict, dict]:
    """Incremental ingestion: re-chunk only documents whose content hash changed since `previous`.

    State maps doc_id -> (sha256, chunks). A document that yields no chunks (an empty or broken export) fails the
    data-quality check: it's reported as blocked and its previous version keeps serving. Removed files are dropped.
    """
    previous = previous or {}
    state, report = {}, {"added": [], "changed": [], "unchanged": [], "removed": [], "blocked": []}
    for p in sorted(Path(policy_dir).glob("*.md")):
        text = p.read_text(encoding="utf-8")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        doc = p.stem
        if doc in previous and previous[doc][0] == digest:
            state[doc] = previous[doc]
            report["unchanged"].append(doc)
            continue
        chunks = chunk_markdown(doc, text)
        if not chunks:
            report["blocked"].append(doc)
            if doc in previous:
                state[doc] = previous[doc]
            continue
        state[doc] = (digest, chunks)
        report["changed" if doc in previous else "added"].append(doc)
    report["removed"] = sorted(set(previous) - {p.stem for p in Path(policy_dir).glob("*.md")})
    return state, report


def chunks_of(state: dict) -> list[Chunk]:
    """Flatten a sync state into the chunk list the retriever indexes (stable order by doc id)."""
    return [c for doc in sorted(state) for c in state[doc][1]]
