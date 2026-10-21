import pytest

SQLITE_DDL = """CREATE TABLE IF NOT EXISTS tickets(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id INTEGER NOT NULL,
  subject TEXT,
  score REAL,
  attachment BLOB,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  resolved_at TEXT
);
CREATE TABLE accounts(id INTEGER PRIMARY KEY, name TEXT NOT NULL);"""


def test_ddl(impl):
    out = impl.translate_ddl(SQLITE_DDL)
    assert "id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY" in out
    assert "account_id INTEGER NOT NULL" in out and "subject TEXT" in out
    assert "score DOUBLE PRECISION" in out and "attachment BYTEA" in out
    assert "created_at TIMESTAMPTZ DEFAULT now()" in out and "resolved_at TIMESTAMPTZ" in out
    assert "CREATE TABLE accounts(id BIGINT PRIMARY KEY, name TEXT NOT NULL);" in out
    assert "AUTOINCREMENT" not in out and "CURRENT_TIMESTAMP" not in out


@pytest.mark.parametrize("src,expected", [
    ("SELECT strftime('%Y-%m', created_at) AS m FROM t",
     "SELECT to_char(created_at, 'YYYY-MM') AS m FROM t"),
    ("SELECT strftime('%Y-%m-%d', created_at) FROM t", "SELECT to_char(created_at, 'YYYY-MM-DD') FROM t"),
    ("SELECT IFNULL(subject, 'none') FROM t WHERE id = ?", "SELECT COALESCE(subject, 'none') FROM t WHERE id = %s"),
    ("SELECT AVG(julianday(resolved_at) - julianday(created_at)) FROM t",
     "SELECT AVG(EXTRACT(EPOCH FROM (resolved_at - created_at)) / 86400) FROM t"),
    ("INSERT OR IGNORE INTO accounts(id, name) VALUES (?, ?)",
     "INSERT INTO accounts(id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING"),
    ("SELECT * FROM t WHERE subject = 'why?' AND id = ?", "SELECT * FROM t WHERE subject = 'why?' AND id = %s"),
])
def test_queries(impl, src, expected):
    assert impl.translate_query(src) == expected


def test_vector_schema(impl):
    stmts = impl.vector_schema("chunks", 1024)
    assert stmts[0] == "CREATE EXTENSION IF NOT EXISTS vector"
    assert "embedding vector(1024) NOT NULL" in stmts[1]
    assert stmts[2] == "CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON chunks USING hnsw (embedding vector_cosine_ops)"
    ivf = impl.vector_schema("chunks", 8, metric="l2", index="ivfflat")[2]
    assert ivf.endswith("USING ivfflat (embedding vector_l2_ops) WITH (lists = 100)")
    with pytest.raises(ValueError):
        impl.vector_schema("chunks", 8, index="annoy")


def test_knn(impl):
    assert impl.knn_query("chunks", 5) == ("SELECT doc_id, chunk, embedding <=> %s AS distance FROM chunks "
                                          "ORDER BY embedding <=> %s LIMIT 5")
    assert "<#>" in impl.knn_query("chunks", 3, metric="ip") and "<->" in impl.knn_query("chunks", 3, metric="l2")
    with pytest.raises(ValueError):
        impl.knn_query("chunks", 0)


def test_table_name_is_validated(impl):
    # Untrusted identifiers: a table name is spliced into SQL, so anything but a plain identifier is refused.
    for bad in ("chunks; DROP TABLE users", "chunks--", "1chunks", "", "a" * 64):
        with pytest.raises(ValueError, match="invalid table name"):
            impl.vector_schema(bad, 8)
        with pytest.raises(ValueError, match="invalid table name"):
            impl.knn_query(bad, 5)
    assert impl.knn_query("tenant_a_chunks", 1).endswith("FROM tenant_a_chunks ORDER BY embedding <=> %s LIMIT 1")
