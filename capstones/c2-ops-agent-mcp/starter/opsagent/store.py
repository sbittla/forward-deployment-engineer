"""Order system of record (SQLite stand-in for the retailer's OMS)."""
import json
import sqlite3
from datetime import date
from pathlib import Path

DDL = """
CREATE TABLE orders(order_id TEXT PRIMARY KEY, customer_email TEXT NOT NULL, status TEXT NOT NULL,
                    delivered_on TEXT, total REAL NOT NULL, items TEXT NOT NULL);
CREATE TABLE refunds(refund_id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL REFERENCES orders,
                     amount REAL NOT NULL CHECK(amount > 0), reason TEXT, approved_by TEXT NOT NULL);
"""


class OrderStore:
    def __init__(self, data: dict):
        self.today = date.fromisoformat(data["today"])
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.executescript(DDL)
        with self.db:
            for o in data["orders"]:
                self.db.execute("INSERT INTO orders VALUES (?,?,?,?,?,?)",
                                (o["order_id"], o["customer_email"], o["status"], o["delivered_on"], o["total"],
                                 json.dumps(o["items"])))
            for r in data.get("refunds", []):
                self.db.execute("INSERT INTO refunds(order_id, amount, reason, approved_by) VALUES (?,?,?,?)",
                                (r["order_id"], r["amount"], r["reason"], r["approved_by"]))

    @classmethod
    def from_json(cls, path) -> "OrderStore":
        raise NotImplementedError

    @staticmethod
    def _row(r) -> dict:
        raise NotImplementedError

    def get_order(self, order_id: str) -> dict | None:
        raise NotImplementedError

    def orders_for(self, email: str) -> list[dict]:
        raise NotImplementedError

    def refunded_total(self, order_id: str) -> float:
        raise NotImplementedError

    def add_refund(self, order_id: str, amount: float, reason: str, approved_by: str) -> int:
        raise NotImplementedError

    def refunds(self) -> list[dict]:
        raise NotImplementedError
