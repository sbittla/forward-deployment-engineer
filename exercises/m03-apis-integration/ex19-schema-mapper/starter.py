from dataclasses import dataclass
from datetime import datetime


@dataclass
class Customer:
    id: str
    name: str
    phone_e164: str | None
    created_at: datetime
    annual_revenue: int | None
    segment: str


@dataclass
class RowError:
    row: int
    field: str
    message: str


def map_records(rows: list[dict]) -> tuple[list[Customer], list[RowError]]:
    raise NotImplementedError
