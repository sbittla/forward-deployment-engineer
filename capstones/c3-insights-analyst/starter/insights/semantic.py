"""Semantic layer: the business definitions the analyst must use, and a generated data dictionary."""
import sqlite3

METRICS = {
    "total_spend": {"sql": "ROUND(SUM(amount_usd), 2)", "table": "transactions",
                    "description": "Sum of USD amounts, refunds (negative amounts) netted out."},
    "refund_count": {"sql": "COUNT(*) ... WHERE amount_usd < 0", "table": "transactions",
                     "description": "Number of refund transactions (negative amounts)."},
    "avg_transaction": {"sql": "ROUND(AVG(amount_usd), 2) ... WHERE amount_usd > 0", "table": "transactions",
                        "description": "Average purchase size in USD, excluding refunds."},
    "monthly_spend": {"sql": "SELECT month, SUM(amount) FROM monthly_spend", "table": "monthly_spend",
                      "description": "Pre-aggregated spend per account, month (YYYY-MM) and category."},
}
ALLOWED_TABLES = ("transactions", "accounts", "monthly_spend")


def _columns(conn: sqlite3.Connection, table: str) -> list[tuple[str, str]]:
    raise NotImplementedError


def schema_prompt(conn: sqlite3.Connection) -> str:
    raise NotImplementedError


def data_dictionary(conn: sqlite3.Connection) -> str:
    raise NotImplementedError
