"""Bronze -> silver -> gold load of the bank's transaction export into SQLite.

Bronze keeps raw rows; silver is typed, de-duplicated (latest `updated_at` wins), currency-normalised and
referentially checked; gold is the `monthly_spend` view the analyst and dashboards query.
"""
import csv
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

FX_TO_USD = {"USD": Decimal("1"), "SEK": Decimal("0.095"), "EUR": Decimal("1.08")}

DDL = """
CREATE TABLE accounts(account_id TEXT PRIMARY KEY, customer_name TEXT NOT NULL, segment TEXT NOT NULL,
                      opened_on TEXT NOT NULL, country TEXT NOT NULL);
CREATE TABLE transactions(txn_id TEXT PRIMARY KEY, account_id TEXT NOT NULL REFERENCES accounts,
                          posted_at TEXT NOT NULL, amount_usd REAL NOT NULL, original_amount REAL NOT NULL,
                          currency TEXT NOT NULL, merchant TEXT, category TEXT NOT NULL);
CREATE VIEW monthly_spend AS
  SELECT account_id, substr(posted_at, 1, 7) AS month, category, ROUND(SUM(amount_usd), 2) AS amount
  FROM transactions GROUP BY account_id, month, category;
"""


@dataclass
class LoadReport:
    bronze_rows: int = 0
    loaded: int = 0
    duplicates: int = 0
    quarantined: list[tuple[str, str]] = field(default_factory=list)   # (txn_id, reason)


def _date(s: str) -> str:
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"unparseable posted_at {s!r}")


def _amount(s: str) -> Decimal:
    try:
        return Decimal(s.replace(",", "").strip())
    except Exception:
        raise ValueError(f"non-numeric amount {s!r}") from None


def load_warehouse(data_dir, conn: sqlite3.Connection | None = None) -> tuple[sqlite3.Connection, LoadReport]:
    data_dir = Path(data_dir)
    conn = conn or sqlite3.connect(":memory:")
    conn.executescript(DDL)
    with open(data_dir / "accounts.csv", newline="", encoding="utf-8") as f:
        accounts = list(csv.DictReader(f))
    with conn:
        conn.executemany("INSERT INTO accounts VALUES (:account_id,:customer_name,:segment,:opened_on,:country)",
                         accounts)
    known = {a["account_id"] for a in accounts}

    with open(data_dir / "transactions.csv", newline="", encoding="utf-8") as f:
        bronze = list(csv.DictReader(f))
    report = LoadReport(bronze_rows=len(bronze))

    latest: dict[str, dict] = {}
    for row in bronze:
        txn = row["txn_id"]
        try:
            if row["account_id"] not in known:
                raise ValueError(f"unknown account {row['account_id']}")
            if row["currency"] not in FX_TO_USD:
                raise ValueError(f"unsupported currency {row['currency']}")
            amount = _amount(row["amount"])
            silver = {
                "txn_id": txn, "account_id": row["account_id"], "posted_at": _date(row["posted_at"]),
                "amount_usd": float((amount * FX_TO_USD[row["currency"]]).quantize(Decimal("0.01"), ROUND_HALF_UP)),
                "original_amount": float(amount), "currency": row["currency"], "merchant": row["merchant"],
                "category": row["category"] or "other", "updated_at": row["updated_at"],
            }
        except ValueError as e:
            report.quarantined.append((txn, str(e)))
            continue
        if txn in latest:
            report.duplicates += 1
            if silver["updated_at"] <= latest[txn]["updated_at"]:
                continue
        latest[txn] = silver

    with conn:
        conn.executemany(
            "INSERT INTO transactions VALUES (:txn_id,:account_id,:posted_at,:amount_usd,:original_amount,"
            ":currency,:merchant,:category)", list(latest.values()))
    report.loaded = len(latest)
    return conn, report
