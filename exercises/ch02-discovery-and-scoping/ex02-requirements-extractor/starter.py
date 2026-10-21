from dataclasses import dataclass


@dataclass(frozen=True)
class Story:
    as_a: str
    i_want: str
    so_that: str
    acceptance_criteria: tuple[str, ...]


def build_prompt(transcript: str) -> tuple[str, str]:
    raise NotImplementedError


def parse_stories(text: str) -> list[Story]:
    raise NotImplementedError


def extract(transcript: str, llm, max_attempts: int = 2) -> list[Story]:
    raise NotImplementedError
