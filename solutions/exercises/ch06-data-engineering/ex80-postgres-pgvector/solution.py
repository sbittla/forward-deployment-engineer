import re

OPCLASS = {"cosine": "vector_cosine_ops", "l2": "vector_l2_ops", "ip": "vector_ip_ops"}
OPERATOR = {"cosine": "<=>", "l2": "<->", "ip": "<#>"}
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,62}")


def _check_table(table: str) -> None:
    if not isinstance(table, str) or not IDENTIFIER.fullmatch(table):
        raise ValueError(f"invalid table name: {table!r}")


def _translate_column(col: str) -> str:
    c = re.sub(r"\bINTEGER PRIMARY KEY AUTOINCREMENT\b", "BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY", col, flags=re.I)
    c = re.sub(r"\bINTEGER PRIMARY KEY\b", "BIGINT PRIMARY KEY", c, flags=re.I)
    c = re.sub(r"\bREAL\b", "DOUBLE PRECISION", c, flags=re.I)
    c = re.sub(r"\bBLOB\b", "BYTEA", c, flags=re.I)
    c = re.sub(r"^(\s*\w+_at\s+)TEXT\b", r"\1TIMESTAMPTZ", c, flags=re.I)
    return re.sub(r"DEFAULT CURRENT_TIMESTAMP", "DEFAULT now()", c, flags=re.I)


def translate_ddl(sqlite_ddl: str) -> str:
    def table(m):
        cols = m.group(2).split(",")
        return m.group(1) + ",".join(_translate_column(c) for c in cols) + m.group(3)
    return re.sub(r"(CREATE TABLE[^(]*\()(.*?)(\)\s*;)", table, sqlite_ddl, flags=re.S | re.I)


def _placeholders(sql: str) -> str:
    out, in_str = [], False
    for ch in sql:
        if ch == "'":
            in_str = not in_str
        out.append("%s" if ch == "?" and not in_str else ch)
    return "".join(out)


def translate_query(sql: str) -> str:
    s = re.sub(r"strftime\('%Y-%m-%d',\s*([^)]+)\)", r"to_char(\1, 'YYYY-MM-DD')", sql)
    s = re.sub(r"strftime\('%Y-%m',\s*([^)]+)\)", r"to_char(\1, 'YYYY-MM')", s)
    s = re.sub(r"\bIFNULL\(", "COALESCE(", s, flags=re.I)
    s = re.sub(r"julianday\(([^)]+)\)\s*-\s*julianday\(([^)]+)\)", r"EXTRACT(EPOCH FROM (\1 - \2)) / 86400", s, flags=re.I)
    if re.match(r"\s*INSERT OR IGNORE INTO", s, re.I):
        s = re.sub(r"INSERT OR IGNORE INTO", "INSERT INTO", s, count=1, flags=re.I).rstrip().rstrip(";") + \
            " ON CONFLICT DO NOTHING"
    return _placeholders(s)


def vector_schema(table: str, dim: int, metric: str = "cosine", index: str = "hnsw") -> list[str]:
    _check_table(table)
    if index not in ("hnsw", "ivfflat"):
        raise ValueError("index must be hnsw or ivfflat")
    idx = f"CREATE INDEX IF NOT EXISTS {table}_embedding_idx ON {table} USING {index} (embedding {OPCLASS[metric]})"
    if index == "ivfflat":
        idx += " WITH (lists = 100)"
    return [
        "CREATE EXTENSION IF NOT EXISTS vector",
        f"CREATE TABLE IF NOT EXISTS {table} (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, "
        f"doc_id TEXT NOT NULL, chunk TEXT NOT NULL, embedding vector({dim}) NOT NULL)",
        idx,
    ]


def knn_query(table: str, k: int, metric: str = "cosine") -> str:
    _check_table(table)
    if not 1 <= k <= 100:
        raise ValueError("k must be between 1 and 100")
    op = OPERATOR[metric]
    return f"SELECT doc_id, chunk, embedding {op} %s AS distance FROM {table} ORDER BY embedding {op} %s LIMIT {k}"
