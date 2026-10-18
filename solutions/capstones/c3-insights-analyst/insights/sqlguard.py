"""Static checks on model-written SQL before it touches the warehouse.

Defence in depth: the connection is also opened read-only in production; this guard gives the model
specific, fixable feedback and blocks anything outside the analyst's remit.
"""
import re

from .semantic import ALLOWED_TABLES

FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|reindex|"
                       r"grant|truncate)\b", re.I)
TABLE_REF = re.compile(r"\b(?:from|join)\s+([A-Za-z_][\w]*)", re.I)
CTE_NAME = re.compile(r"(?:\bwith\b|,)\s*([A-Za-z_][\w]*)\s+as\s*\(", re.I)
LIMIT = re.compile(r"\blimit\s+(\d+)\s*$", re.I)
MAX_ROWS = 1000


class UnsafeSQL(Exception):
    pass


def _strip_comments(sql: str) -> str:
    sql = re.sub(r"--[^\n]*", " ", sql)
    return re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)


def guard_sql(sql: str, allowed_tables=ALLOWED_TABLES, max_rows: int = MAX_ROWS) -> str:
    s = _strip_comments(sql).strip().rstrip(";").strip()
    if ";" in s:
        raise UnsafeSQL("only a single statement is allowed")
    if not re.match(r"^(select|with)\b", s, re.I):
        raise UnsafeSQL("only SELECT queries are allowed")
    m = FORBIDDEN.search(s)
    if m:
        raise UnsafeSQL(f"keyword '{m.group(1).upper()}' is not allowed")
    ctes = {c.lower() for c in CTE_NAME.findall(s)}
    for t in TABLE_REF.findall(s):
        if t.lower() not in ctes and t.lower() not in allowed_tables:
            raise UnsafeSQL(f"table '{t}' is not available; use: {', '.join(allowed_tables)}")
    lim = LIMIT.search(s)
    if lim is None:
        s = f"{s}\nLIMIT {max_rows}"
    elif int(lim.group(1)) > max_rows:
        s = LIMIT.sub(f"LIMIT {max_rows}", s)
    return s
