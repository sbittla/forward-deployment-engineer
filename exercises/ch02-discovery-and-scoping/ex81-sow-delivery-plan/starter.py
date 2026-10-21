import math
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class Task:
    id: str
    name: str
    optimistic: float
    likely: float
    pessimistic: float
    depends_on: tuple = ()
    owner: str = "fde"
    milestone: str | None = None


@dataclass
class Slot:
    start: float
    finish: float
    slack: float
    critical: bool


def pert(task: Task) -> tuple[float, float]:
    raise NotImplementedError


def schedule(tasks: list[Task]) -> dict[str, Slot]:
    raise NotImplementedError


def critical_path(tasks: list[Task]) -> list[str]:
    raise NotImplementedError


def project_estimate(tasks: list[Task]) -> tuple[float, float]:
    raise NotImplementedError


def to_dates(day_offset: int, start: date) -> date:
    raise NotImplementedError


def render_sow(engagement: dict, tasks: list[Task], start: date, rate_per_day: float) -> str:
    raise NotImplementedError
