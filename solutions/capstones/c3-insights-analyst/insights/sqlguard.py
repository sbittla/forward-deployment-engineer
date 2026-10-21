"""Static checks on model-written SQL before it touches the warehouse.

Defence in depth: the connection is also opened read-only in production; this guard gives the model
specific, fixable feedback and blocks anything outside the analyst's remit.
"""
import re

from .semantic import ALLOWED_TABLES

FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|reindex|"
                       r"grant|truncate)\b", re.I)
TABLE_REF = re.compile(r"\b(?:from|join)\s+([A-Za-z_][\w]*)", re.I)
# a FROM list runs to the next clause, and every comma-separated item in it names a table too (FROM a, b)
FROM_LIST = re.compile(r"\bfrom\s+(.*?)(?=\b(?:where|group|order|limit|having|union|join|on)\b|\)|$)", re.I | re.S)
CTE_NAME = re.compile(r"(?:\bwith\b|,)\s*([A-Za-z_][\w]*)\s+as\s*\(", re.I)
LIMIT = re.compile(r"\blimit\s+(\d+)\s*$", re.I)
# SQLite also accepts "t", `t`, [t] and even 'salaries' as a table name; the patterns above see only bare names, so
# quoting is refused outright rather than normalized
STRING_LITERAL = re.compile(r"'(?:[^']|'')*'")
QUOTED_NAME = re.compile(r"[\"`\[]")
NOT_A_BARE_NAME = re.compile(r"\b(?:from|join)\b\s*(?=[^A-Za-z_(\s])", re.I)
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
    bare = STRING_LITERAL.sub("''", s)  # quote characters inside string literals are data, not names
    if QUOTED_NAME.search(bare):
        raise UnsafeSQL("quoted or bracketed names are not allowed; write table and column names bare")
    if NOT_A_BARE_NAME.search(bare):
        raise UnsafeSQL("FROM and JOIN must name an allowed table or a subquery, unquoted")
    ctes = {c.lower() for c in CTE_NAME.findall(bare)}
    tables = TABLE_REF.findall(bare)
    for items in FROM_LIST.findall(bare):
        for item in items.split(",")[1:]:
            m = re.match(r"\s*([A-Za-z_]\w*)", item)
            if m is None and not item.lstrip().startswith("("):
                raise UnsafeSQL("FROM and JOIN must name an allowed table or a subquery, unquoted")
            if m:
                tables.append(m.group(1))
    for t in tables:
        if t.lower() not in ctes and t.lower() not in allowed_tables:
            raise UnsafeSQL(f"table '{t}' is not available; use: {', '.join(allowed_tables)}")
    lim = LIMIT.search(s)
    if lim is None:
        s = f"{s}\nLIMIT {max_rows}"
    elif int(lim.group(1)) > max_rows:
        s = LIMIT.sub(f"LIMIT {max_rows}", s)
    return s
