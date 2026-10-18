import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable


@dataclass
class Check:
    name: str
    fn: Callable
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
        return not any(r.severity == "error" and not r.passed for r in self.results)

    def to_markdown(self) -> str:
        lines = ["| Check | Severity | Status | Failed |", "|---|---|---|---|"]
        lines += [f"| {r.name} | {r.severity} | {'PASS' if r.passed else 'FAIL'} | {r.failed_count} |"
                  for r in self.results]
        return "\n".join(lines) + "\n"


def _row_check(name, pred, severity):
    def fn(rows):
        bad = [i for i, r in enumerate(rows) if pred(r)]
        return not bad, bad
    return Check(name, fn, severity)


def not_null(col, severity="error") -> Check:
    return _row_check(f"not_null({col})", lambda r: r.get(col) in (None, ""), severity)


def unique(col, severity="error") -> Check:
    def fn(rows):
        counts = Counter(r.get(col) for r in rows)
        bad = [i for i, r in enumerate(rows) if counts[r.get(col)] > 1]
        return not bad, bad
    return Check(f"unique({col})", fn, severity)


def in_range(col, lo, hi, severity="error") -> Check:
    return _row_check(f"in_range({col},{lo},{hi})",
                      lambda r: r.get(col) is not None and not lo <= r[col] <= hi, severity)


def matches(col, pattern, severity="error") -> Check:
    rx = re.compile(pattern)
    return _row_check(f"matches({col},{pattern})",
                      lambda r: r.get(col) is not None and not rx.fullmatch(str(r[col])), severity)


def accepted_values(col, values, severity="error") -> Check:
    values = set(values)
    return _row_check(f"accepted_values({col})", lambda r: r.get(col) not in values, severity)


def row_count_between(lo, hi, severity="error") -> Check:
    return Check(f"row_count_between({lo},{hi})", lambda rows: (lo <= len(rows) <= hi, []), severity)


def fresh(col, max_age: timedelta, now: datetime, severity="error") -> Check:
    def fn(rows):
        stamps = [datetime.fromisoformat(r[col]) for r in rows if r.get(col)]
        return bool(stamps) and max(stamps) >= now - max_age, []
    return Check(f"fresh({col})", fn, severity)


def run_checks(rows: list[dict], checks: list[Check]) -> Report:
    results = []
    for c in checks:
        passed, bad = c.fn(rows)
        results.append(Result(c.name, c.severity, passed, len(bad), bad[:5]))
    return Report(results)
