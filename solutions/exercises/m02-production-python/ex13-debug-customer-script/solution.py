"""Invoice report — fixed. Each FIX(n) maps to the customer's numbered bug report."""
import json
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def parse_amount(s):
    # FIX(1): float() rejects thousands separators and is lossy for money; strip commas and use Decimal.
    return Decimal(str(s).replace(",", "").strip())


def fetch_all(client, page_size=50):
    """client.get_page(page, page_size) -> {"items": [...], "total_pages": int}; pages are 1-based."""
    first = client.get_page(1, page_size)
    items = list(first["items"])
    page = 2
    # FIX(2): off-by-one — pages are 1-based and inclusive, so loop while page <= total_pages.
    while page <= first["total_pages"]:
        items.extend(client.get_page(page, page_size)["items"])
        page += 1
    return items


def add_tag(invoice, tag, tags=None):
    # FIX(3): a mutable default list is shared across calls; build a fresh list from the invoice instead.
    tags = list(invoice.get("tags", [])) if tags is None else list(tags)
    tags.append(tag)
    invoice["tags"] = tags
    return invoice


def is_overdue(due_iso, now=None):
    # FIX(4): comparing aware and naive datetimes raises TypeError; normalise both to aware UTC.
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    due = datetime.fromisoformat(due_iso)
    if due.tzinfo is None:
        due = due.replace(tzinfo=timezone.utc)
    return due < now


def total_by_customer(invoices):
    totals = {}
    for inv in invoices:
        totals[inv["customer"]] = totals.get(inv["customer"], Decimal(0)) + parse_amount(inv["amount"])
    # FIX(5): float sums and banker's rounding drift by a cent; sum Decimals and round half-up to cents.
    return {k: v.quantize(CENT, rounding=ROUND_HALF_UP) for k, v in totals.items()}


def remove_paid(invoices_by_id):
    # FIX(6): deleting while iterating a dict raises RuntimeError; iterate over a snapshot of the keys.
    for k in list(invoices_by_id):
        if invoices_by_id[k]["paid"]:
            del invoices_by_id[k]
    return invoices_by_id


def load_config(path):
    # FIX(7): a bare `except Exception` hid corrupt config; only a missing file falls back to defaults.
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"config file {path} is not valid JSON: {e}") from e
