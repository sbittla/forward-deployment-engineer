from dataclasses import dataclass, field
from datetime import date


@dataclass
class Chunk:
    text: str
    start: int
    end: int
    meta: dict = field(default_factory=dict)


def fixed_chunks(text: str, size: int, overlap: int) -> list[Chunk]:
    raise NotImplementedError


def recursive_chunks(text: str, max_chars: int, separators=("\n\n", "\n", ". ", " ")) -> list[Chunk]:
    raise NotImplementedError


def heading_chunks(markdown: str) -> list[Chunk]:
    raise NotImplementedError


def chunk_key(doc_id: str, path: str, text: str) -> str:
    raise NotImplementedError


def plan_reindex(doc_id: str, current: dict[str, str], incoming: list[Chunk]) -> tuple[list[Chunk], list[str]]:
    raise NotImplementedError


def filter_effective(chunks: list[Chunk], on: date) -> list[Chunk]:
    raise NotImplementedError
