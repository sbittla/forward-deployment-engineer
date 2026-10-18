import json
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal

COUNTRY_ALIASES = {"usa": "US", "united states": "US", "u.s.": "US", "uk": "GB", "united kingdom": "GB",
                   "deutschland": "DE", "germany": "DE", "india": "IN"}
REQUIRED = ("event_id", "ts", "type", "product", "country")


def bronze(lines: list[str], source: str, ingested_at: str) -> list[dict]:
    return [{"raw": line, "source": source, "ingested_at": ingested_at, "line_no": i} for i, line in enumerate(lines)]


def _country(raw) -> str | None:
    if not isinstance(raw, str):
        return None
    key = raw.strip().lower()
    if key in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[key]
    if len(key) == 2 and key.isalpha():
        return key.upper()
    return None


def _parse(row: dict) -> dict:
    try:
        rec = json.loads(row["raw"])
    except json.JSONDecodeError:
        raise ValueError("invalid json") from None
    missing = [k for k in REQUIRED if k not in rec]
    if missing:
        raise ValueError(f"missing keys: {', '.join(missing)}")
    if rec["type"] not in ("view", "purchase"):
        raise ValueError(f"unknown type {rec['type']!r}")
    country = _country(rec["country"])
    if country is None:
        raise ValueError(f"unknown country {rec['country']!r}")
    amount = 0.0
    if rec["type"] == "purchase":
        amount = rec.get("amount")
        if isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount < 0:
            raise ValueError("purchase needs a numeric amount >= 0")
        amount = float(amount)
    return {"event_id": rec["event_id"], "ts": rec["ts"], "type": rec["type"], "product": rec["product"],
            "country": country, "amount": amount, "_line": row["line_no"]}


def silver(bronze_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    latest: dict[str, dict] = {}
    quarantine = []
    for row in bronze_rows:
        try:
            ev = _parse(row)
        except ValueError as e:
            quarantine.append({"line_no": row["line_no"], "reason": str(e)})
            continue
        cur = latest.get(ev["event_id"])
        if cur is None or (ev["ts"], ev["_line"]) > (cur["ts"], cur["_line"]):
            latest[ev["event_id"]] = ev
    events = sorted(latest.values(), key=lambda e: (e["ts"], e["event_id"]))
    for e in events:
        del e["_line"]
    return events, quarantine


def gold(events: list[dict]) -> dict:
    revenue = defaultdict(Decimal)
    views, purchases = defaultdict(int), defaultdict(int)
    for e in events:
        if e["type"] == "purchase":
            revenue[(e["ts"][:10], e["country"])] += Decimal(str(e["amount"]))
            purchases[e["product"]] += 1
        else:
            views[e["product"]] += 1
    return {
        "revenue_by_day_country": {k: float(v.quantize(Decimal("0.01"), ROUND_HALF_UP)) for k, v in revenue.items()},
        "conversion_by_product": {p: round(purchases[p] / v, 3) for p, v in views.items() if v},
    }
