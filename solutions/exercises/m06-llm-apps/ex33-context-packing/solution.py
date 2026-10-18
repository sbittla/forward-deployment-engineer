import math
from dataclasses import dataclass, field

MIN_PARTIAL = 50
DOC_HEADER = "\n\n<documents>\n"
DOC_FOOTER = "\n</documents>"


@dataclass
class Packed:
    system: str
    messages: list[dict]
    included_docs: list[str] = field(default_factory=list)
    truncated: list[str] = field(default_factory=list)
    dropped_docs: list[str] = field(default_factory=list)
    tokens: int = 0


def count_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)


def _render_system(system, docs):
    if not docs:
        return system
    return system + DOC_HEADER + "\n".join(f'<doc id="{i}">{t}</doc>' for i, t in docs) + DOC_FOOTER


def pack(system: str, question: str, docs: list[tuple[str, str, float]], history: list[dict],
         budget: int, reserve_output: int) -> Packed:
    available = budget - reserve_output
    question_msg = {"role": "user", "content": question}
    if count_tokens(system) + count_tokens(question) > available:
        raise ValueError("system prompt and question alone exceed the input budget")

    def used(doc_list, msgs):
        return count_tokens(_render_system(system, doc_list)) + sum(count_tokens(m["content"]) for m in msgs)

    chosen: list[tuple[str, str]] = []
    truncated, dropped = [], []
    stop = False
    for doc_id, text, _ in sorted(docs, key=lambda d: -d[2]):
        if stop:
            dropped.append(doc_id)
            continue
        if used(chosen + [(doc_id, text)], [question_msg]) <= available:
            chosen.append((doc_id, text))
            continue
        remaining = available - used(chosen + [(doc_id, "")], [question_msg])
        if remaining >= MIN_PARTIAL:
            chosen.append((doc_id, text[: remaining * 4]))
            truncated.append(doc_id)
        else:
            dropped.append(doc_id)
        stop = True

    pairs = [history[i:i + 2] for i in range(0, len(history), 2)]
    kept: list[list[dict]] = []
    for pair in reversed(pairs):
        candidate = [m for p in [pair] + kept for m in p]
        if used(chosen, candidate + [question_msg]) <= available:
            kept.insert(0, pair)
        else:
            break
    messages = [m for p in kept for m in p] + [question_msg]
    sys_text = _render_system(system, chosen)
    return Packed(sys_text, messages, [d for d, _ in chosen], truncated, dropped, used(chosen, messages))
