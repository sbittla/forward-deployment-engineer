# ex39 · Vector + keyword hybrid search with RRF

**Module:** m07 · **Covers:** R10 Retrieval & vector search · **Time:** 50 min

## Scenario
Keyword search nails identifiers; vector search handles paraphrases. Customers want both. Reciprocal Rank Fusion
(RRF) combines rankings without having to calibrate incomparable scores — the default in many vector databases.

## Your task
1. `VectorIndex(dim=256)` using `fde_kit.hash_embed` and `fde_kit.cosine`:
   `add(doc_id, text)`, `search(query, k) -> [(doc_id, cosine)]` sorted desc then id; exclude scores ≤ 0.
2. `rrf(rankings: list[list[str]], k=60) -> [(doc_id, score)]` — `score(d) = Σ 1 / (k + rank_i(d))` with 1-based
   ranks over every ranking that contains `d`. Sort by score desc then doc_id.
3. `hybrid_search(query, keyword_fn, vector_fn, k=5, depth=20)` — call both retrieval functions with
   `(query, depth)`, fuse their id lists with `rrf`, return the top `k` `(doc_id, score)`.
4. `explain_fusion(query, keyword_fn, vector_fn, doc_id, depth=20)` →
   `{"keyword_rank": int | None, "vector_rank": int | None}` (1-based).

In production you would plug real embeddings (and a real vector DB) into the same interfaces.
