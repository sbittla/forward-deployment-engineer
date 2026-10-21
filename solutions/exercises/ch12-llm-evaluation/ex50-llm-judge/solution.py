import json
import re
from dataclasses import dataclass


@dataclass
class Verdict:
    score: int
    reasoning: str


def judge(llm, question: str, answer: str, reference: str, rubric: str) -> Verdict:
    system = (
        "You are a strict grader of customer-support answers.\n"
        f"Rubric (score 1-5):\n{rubric}\n"
        'Reply with only JSON: {"reasoning": "<one or two sentences>", "score": <integer 1-5>}. '
        "Write the reasoning before deciding the score."
    )
    user = f"Question:\n{question}\n\nReference answer:\n{reference}\n\nCandidate answer:\n{answer}"
    text = llm.complete([{"role": "user", "content": user}], system=system).text
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("judge reply contained no JSON")
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(f"judge reply is not valid JSON: {e}") from None
    score = data.get("score")
    if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
        raise ValueError(f"invalid score {score!r}")
    return Verdict(score, str(data.get("reasoning", "")))


def agreement(judge_scores: list[int], human_scores: list[int], threshold: int = 4) -> dict:
    n = len(judge_scores)
    exact = sum(a == b for a, b in zip(judge_scores, human_scores)) / n
    within = sum(abs(a - b) <= 1 for a, b in zip(judge_scores, human_scores)) / n
    jp = [s >= threshold for s in judge_scores]
    hp = [s >= threshold for s in human_scores]
    po = sum(a == b for a, b in zip(jp, hp)) / n
    pj, ph = sum(jp) / n, sum(hp) / n
    pe = pj * ph + (1 - pj) * (1 - ph)
    kappa = 1.0 if pe == 1 else (po - pe) / (1 - pe)
    return {"exact": round(exact, 3), "within_1": round(within, 3), "kappa": round(kappa, 3)}


def _ask(llm, question, first, second) -> str:
    system = "Compare two answers to the same question. Reply with only 1 or 2: the number of the better answer."
    user = f"Question: {question}\n\nAnswer 1:\n{first}\n\nAnswer 2:\n{second}"
    return llm.complete([{"role": "user", "content": user}], system=system, max_tokens=2).text.strip()


def pairwise(llm, question: str, a: str, b: str) -> str:
    r1 = _ask(llm, question, a, b)   # "1" means A
    r2 = _ask(llm, question, b, a)   # "1" means B
    w1 = {"1": "A", "2": "B"}.get(r1)
    w2 = {"1": "B", "2": "A"}.get(r2)
    return w1 if w1 is not None and w1 == w2 else "tie"
