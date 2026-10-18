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
    return [(r[1], r[2] or "") for r in conn.execute(f"PRAGMA table_info({table})")]


def schema_prompt(conn: sqlite3.Connection) -> str:
    lines = ["Tables (SQLite):"]
    for t in ALLOWED_TABLES:
        cols = ", ".join(f"{c} {ty}".strip() for c, ty in _columns(conn, t))
        lines.append(f"- {t}({cols})")
    lines.append("Business metric definitions (use these exactly):")
    lines += [f"- {name}: {m['description']} SQL: {m['sql']}" for name, m in METRICS.items()]
    lines.append("Dates are ISO strings (YYYY-MM-DD). All money is in USD in column amount_usd.")
    return "\n".join(lines)


def data_dictionary(conn: sqlite3.Connection) -> str:
    out = ["# Data dictionary", ""]
    for t in ALLOWED_TABLES:
        out += [f"## {t}", "| Column | Type |", "|---|---|"]
        out += [f"| {c} | {ty or 'n/a'} |" for c, ty in _columns(conn, t)]
        out.append("")
    out += ["## Metrics", "| Metric | Definition |", "|---|---|"]
    out += [f"| {n} | {m['description']} |" for n, m in METRICS.items()]
    return "\n".join(out) + "\n"
