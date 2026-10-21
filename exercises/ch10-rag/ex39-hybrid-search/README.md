# ex39 · Vector + keyword hybrid search with RRF

**Chapter:** 10 · Retrieval-Augmented Generation (RAG) (`exercises/ch10-rag/`) · **Covers:** R10 Retrieval & vector search

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

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch10-rag/ex39-hybrid-search`.
- **Expected output:** all 5 tests fail against the starter; when you're done, all 5 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch10-rag/ex39-hybrid-search`: all 5 pass.
- **Tests:** `test_hybrid.py` (5 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The hashing embedder and brute-force cosine scan make tests reproducible but carry no
  meaning and don't scale. Production needs a real embedding model chosen on your query set, a vector index that
  stores the model identifier with every vector, and permission and tenant filters applied inside both retrievers
  before fusion.

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
Implement exercises/ch10-rag/ex39-hybrid-search/starter.py so that test_hybrid.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `VectorIndex`,
`rrf`, `hybrid_search`, `explain_fusion`. Constraints: Python 3.11+, the standard library and the repo's fde_kit
package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done,
run `pytest exercises/ch10-rag/ex39-hybrid-search` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Vector + keyword hybrid search with RRF" as a senior forward deployed engineer would before
it ships to a customer. Specifically: Are ranks 1-based? Are ties sorted deterministically? When would a weighted
fusion beat plain RRF for this customer? Rank findings by customer impact, quote the line for each, and say which
ones a test should catch.
```
