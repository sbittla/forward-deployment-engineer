"""Invoice report — written by a contractor, handed to you by the customer. Contains bugs."""
import json
from datetime import datetime


def parse_amount(s):
    return float(s)


def fetch_all(client, page_size=50):
    """client.get_page(page, page_size) -> {"items": [...], "total_pages": int}; pages are 1-based."""
    first = client.get_page(1, page_size)
    items = list(first["items"])
    page = 2
    while page < first["total_pages"]:
        items.extend(client.get_page(page, page_size)["items"])
        page += 1
    return items


def add_tag(invoice, tag, tags=[]):
    tags.append(tag)
    invoice["tags"] = tags
    return invoice


def is_overdue(due_iso, now=None):
    now = now or datetime.now()
    return datetime.fromisoformat(due_iso) < now


def total_by_customer(invoices):
    totals = {}
    for inv in invoices:
        totals[inv["customer"]] = totals.get(inv["customer"], 0) + parse_amount(inv["amount"])
    return {k: round(v, 2) for k, v in totals.items()}


def remove_paid(invoices_by_id):
    for k in invoices_by_id:
        if invoices_by_id[k]["paid"]:
            del invoices_by_id[k]
    return invoices_by_id


def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}
