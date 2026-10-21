# ex39 · Vector + keyword hybrid search with RRF

**Module:** m07 · **Covers:** R10 Retrieval & vector search · **Time:** 50 min

## Learning objectives
- Fuse keyword and vector rankings with reciprocal rank fusion.
- Explain why RRF avoids calibrating incomparable scores.
- Debug fused results by inspecting each retriever's rank.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Vector + keyword hybrid search with
RRF". Before I write code, teach me vector search with cosine similarity, hybrid retrieval, reciprocal rank fusion,
and the k constant. Use short Python examples that are not the exercise solution. Then ask me three questions to
check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m07-retrieval-rag/ex39-hybrid-search/starter.py so that test_hybrid.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `VectorIndex`,
`rrf`, `hybrid_search`, `explain_fusion`. Constraints: Python 3.11+, the standard library and the repo's fde_kit
package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done,
run `pytest exercises/m07-retrieval-rag/ex39-hybrid-search` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Vector + keyword hybrid search with RRF" as a senior forward deployed engineer would before
it ships to a customer. Specifically: Are ranks 1-based? Are ties sorted deterministically? When would a weighted
fusion beat plain RRF for this customer? Rank findings by customer impact, quote the line for each, and say which
ones a test should catch.
```
