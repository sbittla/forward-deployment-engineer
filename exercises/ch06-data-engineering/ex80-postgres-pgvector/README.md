# ex80 · SQLite to Postgres portability and pgvector

**Chapter:** 6 · Data Engineering (`exercises/ch06-data-engineering/`) · **Covers:** R03 SQL, R10 Vector search, R28 Architecture · **Hands-on:** Postgres, SQL, vector DB ·
**Time:** 60 min

## Learning objectives
- Port SQLite schemas and queries to Postgres.
- Generate pgvector DDL, indexes and similarity queries.
- Avoid placeholder and quoting bugs during translation.

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
5. Both `vector_schema` and `knn_query` splice `table` into SQL, so treat it as untrusted: unless it matches
   `[A-Za-z_][A-Za-z0-9_]{0,62}` (a plain Postgres identifier of at most 63 characters), raise
   `ValueError("invalid table name: ...")` before building any SQL. Values (`%s`) stay parameters.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch06-data-engineering/ex80-postgres-pgvector`.
- **Expected output:** all 10 tests fail against the starter; when you're done, all 10 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch06-data-engineering/ex80-postgres-pgvector`: all
  10 pass.
- **Tests:** `test_postgres.py` (10 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The translators are regex-based and cover only the listed constructs, and the pgvector
  statements are generated, not run. A production port is tested against a real Postgres with the extension
  installed, uses a migration tool and parameterized queries, and measures recall (including filtered queries) before
  choosing the index and its `ef_search` or `lists` settings.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "SQLite to Postgres portability and
pgvector". Before I write code, teach me SQLite vs Postgres differences, psycopg placeholders, pgvector types,
distance operators and HNSW/IVFFlat indexes. Use short Python examples that are not the exercise solution. Then ask
me three questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch06-data-engineering/ex80-postgres-pgvector/starter.py so that test_postgres.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`translate_ddl`, `translate_query`, `vector_schema`, `knn_query`. Constraints: Python 3.11+, the standard library
and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or
fde_kit. When you're done, run `pytest exercises/ch06-data-engineering/ex80-postgres-pgvector` and show me the
output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "SQLite to Postgres portability and pgvector" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Are '?' characters inside string literals left alone? Does the distance
operator match the chosen metric? Which translations need a human because they change semantics? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
