# ex80 · SQLite to Postgres portability and pgvector

**Module:** m13 · **Covers:** R03 SQL, R10 Vector search, R28 Architecture · **Hands-on:** Postgres, SQL, vector DB ·
**Time:** 60 min

## Scenario
You prototyped on SQLite (fast, zero setup). The customer's platform team only runs managed Postgres (RDS, Cloud SQL,
Azure Database for PostgreSQL), and their security team won't approve a separate vector database, so embeddings go
into Postgres with the `pgvector` extension. Port the schema and queries and generate the vector DDL and queries.

## Your task
1. `translate_ddl(sqlite_ddl) -> str`, applied per column definition inside `CREATE TABLE` statements:
   - `INTEGER PRIMARY KEY AUTOINCREMENT` → `BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY`
   - `INTEGER PRIMARY KEY` → `BIGINT PRIMARY KEY`
   - `REAL` → `DOUBLE PRECISION`; `BLOB` → `BYTEA`
   - a `TEXT` column whose name ends in `_at` → `TIMESTAMPTZ`; `DEFAULT CURRENT_TIMESTAMP` → `DEFAULT now()`
   - `CREATE TABLE IF NOT EXISTS` stays; everything else is unchanged
2. `translate_query(sql) -> str`:
   - `strftime('%Y-%m', X)` → `to_char(X, 'YYYY-MM')` and `strftime('%Y-%m-%d', X)` → `to_char(X, 'YYYY-MM-DD')`
   - `IFNULL(` → `COALESCE(`
   - `julianday(B) - julianday(A)` → `EXTRACT(EPOCH FROM (B - A)) / 86400`
   - `INSERT OR IGNORE INTO` → `INSERT INTO` … with ` ON CONFLICT DO NOTHING` appended to the statement
   - `?` placeholders → `%s` (psycopg style), but not inside quoted strings
3. `vector_schema(table, dim, metric="cosine", index="hnsw") -> list[str]`:
   `CREATE EXTENSION IF NOT EXISTS vector`,
   `CREATE TABLE IF NOT EXISTS {table} (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, doc_id TEXT NOT NULL, chunk TEXT NOT NULL, embedding vector({dim}) NOT NULL)`,
   `CREATE INDEX IF NOT EXISTS {table}_embedding_idx ON {table} USING {index} (embedding {opclass})` where opclass is
   `vector_cosine_ops` / `vector_l2_ops` / `vector_ip_ops` for metric `cosine` / `l2` / `ip`. `index` must be
   `hnsw` or `ivfflat` (ivfflat adds ` WITH (lists = 100)`); anything else raises `ValueError`.
4. `knn_query(table, k, metric="cosine") -> str` using operators `<=>` (cosine), `<->` (l2), `<#>` (ip):
   `SELECT doc_id, chunk, embedding {op} %s AS distance FROM {table} ORDER BY embedding {op} %s LIMIT {k}`.
   `k` must be 1–100.
