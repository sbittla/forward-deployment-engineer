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
    raise NotImplementedError


def chunk_markdown(doc_id: str, markdown: str) -> list[Chunk]:
    raise NotImplementedError


def load_corpus(policy_dir) -> list[Chunk]:
    raise NotImplementedError
