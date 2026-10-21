"""Pick few-shot examples per query: relevant, diverse, label-balanced and within a token budget."""
from html import escape

from fde_kit.text import cosine, hash_embed

DUPLICATE_SIM = 0.95


def approx_tokens(example: dict) -> int:
    return max(1, (len(example["input"]) + len(example["output"])) // 4)


def select_examples(query: str, pool: list[dict], k: int = 3, lam: float = 0.7,
                    max_tokens: int | None = None) -> list[dict]:
    """Maximal marginal relevance with near-duplicate suppression and a token budget.

    Returned least relevant first, so the most relevant example sits closest to the query.
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    q = hash_embed(query)
    vecs = [hash_embed(ex["input"]) for ex in pool]
    rel = [cosine(q, v) for v in vecs]
    chosen: list[int] = []
    budget = max_tokens
    candidates = list(range(len(pool)))
    while candidates and len(chosen) < k:
        def mmr(i):
            redundancy = max((cosine(vecs[i], vecs[j]) for j in chosen), default=0.0)
            return (lam * rel[i] - (1 - lam) * redundancy, -i)
        best = max(candidates, key=mmr)
        candidates.remove(best)
        if any(cosine(vecs[best], vecs[j]) >= DUPLICATE_SIM for j in chosen):
            continue
        cost = approx_tokens(pool[best])
        if budget is not None and cost > budget:
            continue
        chosen.append(best)
        if budget is not None:
            budget -= cost
    return [pool[i] for i in sorted(chosen, key=lambda i: (rel[i], -i))]


def ensure_label_coverage(selected: list[dict], pool: list[dict], labels: list[str], query: str,
                          max_tokens: int | None = None) -> list[dict]:
    """Swap in the most relevant example for any label missing from `selected`, replacing an example whose label is
    over-represented. Never adds an example (k still holds) and never exceeds `max_tokens`."""
    q = hash_embed(query)
    out = list(selected)
    for label in labels:
        if any(ex["output"] == label for ex in out):
            continue
        options = [ex for ex in pool if ex["output"] == label and ex not in out]
        if not options:
            continue
        best = max(options, key=lambda ex: cosine(q, hash_embed(ex["input"])))
        counts = {}
        for ex in out:
            counts[ex["output"]] = counts.get(ex["output"], 0) + 1
        used = sum(approx_tokens(ex) for ex in out)
        # replace the least relevant example whose label is over-represented and whose swap fits the budget;
        # if none qualifies, the label stays uncovered: coverage never grows the list past k or the budget
        for i, ex in enumerate(out):
            fits = max_tokens is None or used - approx_tokens(ex) + approx_tokens(best) <= max_tokens
            if counts[ex["output"]] > 1 and fits:
                out[i] = best
                break
    return sorted(out, key=lambda ex: cosine(q, hash_embed(ex["input"])))


def format_examples(examples: list[dict]) -> str:
    parts = [f"<example>\n<input>{escape(ex['input'], quote=False)}</input>\n"
             f"<output>{escape(ex['output'], quote=False)}</output>\n</example>" for ex in examples]
    return "<examples>\n" + "\n".join(parts) + "\n</examples>"


def build_messages(query: str, pool: list[dict], k: int = 3) -> list[dict]:
    shots = format_examples(select_examples(query, pool, k))
    content = (f"{shots}\n\nClassify the ticket below the same way as the examples. Reply with the label only.\n"
               f"<ticket>{escape(query, quote=False)}</ticket>")
    return [{"role": "user", "content": content}]
