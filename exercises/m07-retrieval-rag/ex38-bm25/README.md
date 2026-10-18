# ex38 · BM25 from scratch

**Module:** m07 · **Covers:** R10 Retrieval · **Time:** 45 min

## Scenario
Embeddings miss exact identifiers — error codes, policy numbers, SKUs — which are exactly what support agents
search for. BM25 is the workhorse keyword ranker inside Elasticsearch/OpenSearch and most hybrid systems. Knowing
its knobs lets you explain to a customer *why* a document ranked first.

## Your task
`BM25(k1=1.5, b=0.75)` using `fde_kit.tokenize` (stopwords dropped):
- `fit(docs: list[tuple[id, text]])`
- `idf(term) = ln((N - df + 0.5) / (df + 0.5) + 1)` (0 for unseen terms is fine — the formula gives a small positive
  value; keep the formula)
- `score(query, doc_id) = Σ_{t in query tokens} idf(t) · tf·(k1+1) / (tf + k1·(1 − b + b·|d|/avgdl))`
  (repeated query terms count once each time they appear)
- `search(query, k=10) -> list[(doc_id, score)]` — only docs with score > 0, sorted by score desc then doc_id.
- `explain(query, doc_id) -> dict[term, contribution]` — per-term contributions that sum to `score`.
