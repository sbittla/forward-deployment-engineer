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
    raise NotImplementedError


def chunk_markdown(doc_id: str, markdown: str) -> list[Chunk]:
    raise NotImplementedError


def load_corpus(policy_dir) -> list[Chunk]:
    raise NotImplementedError


def sync_corpus(policy_dir, previous: dict | None = None) -> tuple[dict, dict]:
    """Incremental ingestion: re-chunk only documents whose content hash changed since `previous`.

    State maps doc_id -> (sha256, chunks). A document that yields no chunks (an empty or broken export) fails the
    data-quality check: it's reported as blocked and its previous version keeps serving. Removed files are dropped.
    """
    raise NotImplementedError


def chunks_of(state: dict) -> list[Chunk]:
    """Flatten a sync state into the chunk list the retriever indexes (stable order by doc id)."""
    raise NotImplementedError
