from dataclasses import dataclass, field


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
