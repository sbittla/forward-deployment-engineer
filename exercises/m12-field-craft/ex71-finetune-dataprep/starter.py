import json
import math
import random
import re


def select(convs: list[dict], min_csat: int = 4) -> list[dict]:
    raise NotImplementedError


def to_example(conv: dict, system: str) -> dict:
    raise NotImplementedError


def dedupe(examples: list[dict]) -> list[dict]:
    raise NotImplementedError


def split(examples: list[dict], intents: list[str], val_ratio: float = 0.2, seed: int = 0):
    raise NotImplementedError


def max_tokens_filter(examples: list[dict], limit: int) -> list[dict]:
    raise NotImplementedError


def write_jsonl(examples: list[dict], path) -> None:
    raise NotImplementedError


def stats(train: list[dict], val: list[dict]) -> dict:
    raise NotImplementedError
