import json
from collections import defaultdict


def parse(lines: list[str]) -> tuple[list[dict], int]:
    raise NotImplementedError


def error_rate_by_minute(records: list[dict]) -> dict:
    raise NotImplementedError


def first_errors(records: list[dict]) -> dict:
    raise NotImplementedError


def root_cause(records: list[dict], deps: dict[str, list[str]]) -> str:
    raise NotImplementedError


def timeline(records: list[dict], request_id: str) -> list[str]:
    raise NotImplementedError


def incident_summary(lines: list[str], deps: dict[str, list[str]]) -> str:
    raise NotImplementedError
