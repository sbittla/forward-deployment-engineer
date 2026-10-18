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
    raise NotImplementedError


def guard_sql(sql: str, allowed_tables=ALLOWED_TABLES, max_rows: int = MAX_ROWS) -> str:
    raise NotImplementedError
