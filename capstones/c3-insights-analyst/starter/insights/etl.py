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
    raise NotImplementedError


def _amount(s: str) -> Decimal:
    raise NotImplementedError


def load_warehouse(data_dir, conn: sqlite3.Connection | None = None) -> tuple[sqlite3.Connection, LoadReport]:
    raise NotImplementedError
