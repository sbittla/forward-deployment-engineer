import re
from dataclasses import dataclass, field

ABSTAIN_TEXT = "I can't find that in the provided documents."
CITE = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")


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
    system = (
        "You answer questions about insurance policies using ONLY the numbered sources provided.\n"
        "After every claim, cite the supporting source number in square brackets, like [1] or [1][3].\n"
        f"If the sources do not contain the answer, reply exactly: {ABSTAIN_TEXT}"
    )
    # Retrieved text is data: keep it on its own line so it can't forge another "[n] (doc_id)" source line.
    lines = [f"[{i}] ({s.doc_id}) {' '.join(s.text.split())}" for i, s in enumerate(sources, 1)]
    user = "Sources:\n" + "\n".join(lines) + f"\n\nQuestion: {question}"
    return system, user


def answer(question: str, retrieve, llm, k: int = 4, min_score: float = 0.2) -> Answer:
    sources = retrieve(question, k)
    if not sources or sources[0].score < min_score:
        return Answer(ABSTAIN_TEXT, abstained=True, grounded=True)
    system, user = build_prompt(question, sources)
    text = llm.complete([{"role": "user", "content": user}], system=system).text.strip()
    if text == ABSTAIN_TEXT:
        return Answer(text, abstained=True, grounded=True)

    citations, invalid = [], []

    def keep_valid(m):
        nums = [int(n) for n in re.split(r"\s*,\s*", m.group(1))]
        good = []
        for n in nums:
            if 1 <= n <= len(sources):
                good.append(n)
                if sources[n - 1].doc_id not in citations:
                    citations.append(sources[n - 1].doc_id)
            elif n not in invalid:
                invalid.append(n)
        return "".join(f"[{n}]" for n in good)

    cleaned = re.sub(r"\s+([.,;])", r"\1", CITE.sub(keep_valid, text))
    return Answer(cleaned, citations, False, bool(citations) and not invalid, invalid)
