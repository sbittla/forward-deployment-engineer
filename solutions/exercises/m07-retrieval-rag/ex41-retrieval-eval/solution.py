import math

METRICS = ("recall", "precision", "mrr", "ndcg")


def recall_at_k(ranked: list[str], relevant: dict[str, int], k: int) -> float:
    rel = {d for d, g in relevant.items() if g >= 1}
    if not rel:
        return 0.0
    return len(rel & set(ranked[:k])) / len(rel)


def precision_at_k(ranked: list[str], relevant: dict[str, int], k: int) -> float:
    return sum(1 for d in ranked[:k] if relevant.get(d, 0) >= 1) / k


def mrr(ranked: list[str], relevant: dict[str, int]) -> float:
    for i, d in enumerate(ranked, 1):
        if relevant.get(d, 0) >= 1:
            return 1 / i
    return 0.0


def _dcg(grades: list[int]) -> float:
    return sum((2 ** g - 1) / math.log2(i + 1) for i, g in enumerate(grades, 1))


def ndcg_at_k(ranked: list[str], relevant: dict[str, int], k: int) -> float:
    ideal = _dcg(sorted((g for g in relevant.values() if g >= 1), reverse=True)[:k])
    if ideal == 0:
        return 0.0
    return _dcg([relevant.get(d, 0) for d in ranked[:k]]) / ideal


def evaluate(retrieve, qrels: dict, k: int) -> dict:
    per = {}
    for qid, q in qrels.items():
        ranked = list(retrieve(q["query"], k))
        rel = q["relevant"]
        per[qid] = {
            "recall": round(recall_at_k(ranked, rel, k), 4),
            "precision": round(precision_at_k(ranked, rel, k), 4),
            "mrr": round(mrr(ranked, rel), 4),
            "ndcg": round(ndcg_at_k(ranked, rel, k), 4),
        }
    mean = {m: round(sum(p[m] for p in per.values()) / len(per), 4) for m in METRICS}
    return {"per_query": per, "mean": mean}


def compare(a: dict, b: dict, names=("A", "B")) -> str:
    lines = [f"| Metric | {names[0]} | {names[1]} | Δ |", "|---|---|---|---|"]
    for m in METRICS:
        x, y = a["mean"][m], b["mean"][m]
        lines.append(f"| {m} | {x:.4f} | {y:.4f} | {y - x:+.4f} |")
    return "\n".join(lines) + "\n"
