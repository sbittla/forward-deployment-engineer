from dataclasses import dataclass


@dataclass
class Verdict:
    score: int
    reasoning: str


def judge(llm, question: str, answer: str, reference: str, rubric: str) -> Verdict:
    raise NotImplementedError


def agreement(judge_scores: list[int], human_scores: list[int], threshold: int = 4) -> dict:
    raise NotImplementedError


def pairwise(llm, question: str, a: str, b: str) -> str:
    raise NotImplementedError
