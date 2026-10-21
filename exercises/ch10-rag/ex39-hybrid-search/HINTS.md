# ex39 hints · Vector + keyword hybrid search with RRF

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Start with `rrf`. It's pure, and `test_rrf_math` gives the exact scores. For each ranking, `enumerate(ranking, 1)`
gives 1-based ranks; add `1 / (k + rank)` to that doc's running total in a dict.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- `VectorIndex` stores `doc_id -> hash_embed(text, dim)`. `search` embeds the query the same way, scores every doc
  with `cosine`, drops scores of 0 or below, and sorts.
- `hybrid_search` calls both retrieval functions with `(query, depth)`, passes the two id lists to `rrf`, and slices
  the top `k`.
- `explain_fusion` asks the same two functions for their lists and reports where the doc sits in each (1-based), or
  `None`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Every list sorts by `(-score, doc_id)`, which makes ties deterministic. `rrf([["y"], ["x"]])` must return `x`
  first.
- Fusion uses **ranks**, never the raw scores. BM25 scores and cosines are on different scales, which is the whole
  reason RRF exists.
- Pass `depth` to the retrievers, not `k`: you want a deep candidate pool to fuse, then a short final list.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_vector_index` | Scores of 0 or below kept; results not sorted descending |
| `test_rrf_math` | 0-based ranks, so the top doc scores `1/60` instead of `1/61` |
| `test_rrf_tie_break` | Ties left in insertion order instead of sorted by id |
| `test_hybrid` | Raw scores fused instead of ranks; result not cut to `k` |
| `test_hybrid_calls_with_depth` | Retrievers called with `k` instead of `depth` |
| `test_search_as_never_crosses_tenants` | Ranked everything and then dropped foreign chunks with too small a `k`; tenant compared loosely; scores differ from `search` |
| `test_search_as_fails_closed` | A chunk with no ACL, tenant or groups treated as public; a user without a tenant allowed through instead of `PermissionError` |
