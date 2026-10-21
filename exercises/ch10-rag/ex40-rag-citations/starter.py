from dataclasses import dataclass, field

ABSTAIN_TEXT = "I can't find that in the provided documents."


@dataclass
class Source:
    doc_id: str
    text: str
    score: float


@dataclass
class Answer:
    text: str
    citations: list[str] = field(default_factory=list)
    abstained: bool = False
    grounded: bool = False
    invalid_citations: list[int] = field(default_factory=list)


def build_prompt(question: str, sources: list[Source]) -> tuple[str, str]:
    raise NotImplementedError


def answer(question: str, retrieve, llm, k: int = 4, min_score: float = 0.2) -> Answer:
    raise NotImplementedError
