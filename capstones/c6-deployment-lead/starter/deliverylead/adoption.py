"""Adoption funnel, lagging teams and difference-in-differences impact."""
from collections import defaultdict


def _mean(xs):
    raise NotImplementedError


def funnel(events: list[dict]) -> dict:
    raise NotImplementedError


def lagging_teams(events: list[dict], threshold: float = 0.5) -> list[tuple[str, float]]:
    raise NotImplementedError


def diff_in_diff(pre_t, post_t, pre_c, post_c) -> dict:
    raise NotImplementedError
