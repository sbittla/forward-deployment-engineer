"""Ticket export utilities: the agent's overnight PR after human review."""
import csv
import json
import os
from collections import Counter


def find_tickets(conn, customer):
    # Parameterised: the driver quotes the value, so input can never change the query's structure.
    return conn.execute("SELECT id, subject, status FROM tickets WHERE customer = ? ORDER BY id", (customer,)).fetchall()


def export_csv(rows, filename, out_dir):
    base = os.path.realpath(out_dir)
    path = os.path.realpath(os.path.join(base, filename))
    if os.path.dirname(path) != base or "\\" in filename or "/" in filename:
        raise ValueError(f"refusing to write outside {out_dir}: {filename!r}")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "subject", "status"])
        w.writerows(rows)
    return path


def fetch_all(client, total_pages):
    items = []
    for page in range(1, total_pages + 1):   # pages are 1-based and inclusive
        items += client.get_page(page)
    return items


def call_api(client, token, log):
    log.append("calling export API")         # never log credentials
    return client.export(token)


def load_tickets(path):
    with open(path, encoding="utf-8") as f:  # FileNotFoundError propagates on purpose
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"{path} is not valid JSON: {e}") from e


def tag_counts(rows, counts=None):
    counts = Counter(counts or {})
    for r in rows:
        counts.update(r.get("tags", []))
    return dict(counts)
