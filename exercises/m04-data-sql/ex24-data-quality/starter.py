from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable


@dataclass
class Check:
    name: str
    fn: Callable  # (rows) -> (passed: bool, failing_indices: list[int])
    severity: str = "error"


@dataclass
class Result:
    name: str
    severity: str
    passed: bool
    failed_count: int
    sample_rows: list[int] = field(default_factory=list)


@dataclass
class Report:
    results: list[Result]

    @property
    def ok(self) -> bool:
        raise NotImplementedError

    def to_markdown(self) -> str:
        raise NotImplementedError


def not_null(col, severity="error") -> Check:
    raise NotImplementedError


def unique(col, severity="error") -> Check:
    raise NotImplementedError


def in_range(col, lo, hi, severity="error") -> Check:
    raise NotImplementedError


def matches(col, pattern, severity="error") -> Check:
    raise NotImplementedError


def accepted_values(col, values, severity="error") -> Check:
    raise NotImplementedError


def row_count_between(lo, hi, severity="error") -> Check:
    raise NotImplementedError


def fresh(col, max_age: timedelta, now: datetime, severity="error") -> Check:
    raise NotImplementedError


def run_checks(rows: list[dict], checks: list[Check]) -> Report:
    raise NotImplementedError


def pseudonymise(value: str, key: bytes) -> str:
    raise NotImplementedError


def checks_from_contract(contract: dict) -> list[Check]:
    raise NotImplementedError
