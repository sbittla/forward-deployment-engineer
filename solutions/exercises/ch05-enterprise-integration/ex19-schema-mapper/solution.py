import re
from dataclasses import dataclass
from datetime import datetime, timezone


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


def _phone(raw: str) -> str | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        raise ValueError(f"not a US phone number: {raw!r}")
    return "+1" + digits


def _created(raw: str) -> datetime:
    try:
        dt = datetime.strptime(raw.strip(), "%Y-%m-%dT%H:%M:%S.%f%z")
    except (ValueError, AttributeError):
        raise ValueError(f"unparseable timestamp {raw!r}") from None
    return dt.astimezone(timezone.utc)


def _revenue(raw: str) -> int | None:
    raw = (raw or "").strip().replace(",", "")
    if not raw:
        return None
    try:
        return int(float(raw))
    except ValueError:
        raise ValueError(f"non-numeric revenue {raw!r}") from None


def _segment(rev: int | None) -> str:
    if rev is None:
        return "unknown"
    if rev >= 100_000_000:
        return "enterprise"
    if rev >= 10_000_000:
        return "mid_market"
    return "smb"


def map_records(rows: list[dict]) -> tuple[list[Customer], list[RowError]]:
    customers, errors = [], []
    for i, row in enumerate(rows):
        row_errors, vals = [], {}
        vals["id"] = (row.get("Id") or "").strip()
        if not vals["id"]:
            row_errors.append(RowError(i, "id", "Id is required"))
        vals["name"] = " ".join((row.get("AccountName") or "").split())
        if not vals["name"]:
            row_errors.append(RowError(i, "name", "AccountName is required"))
        for field, fn, src in (("phone_e164", _phone, "Phone"), ("created_at", _created, "CreatedDate"),
                               ("annual_revenue", _revenue, "AnnualRevenue")):
            try:
                vals[field] = fn(row.get(src, ""))
            except ValueError as e:
                row_errors.append(RowError(i, field, str(e)))
        if row_errors:
            errors += row_errors
            continue
        customers.append(Customer(segment=_segment(vals["annual_revenue"]), **vals))
    return customers, errors
