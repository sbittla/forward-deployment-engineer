# ex38 · BM25 from scratch

**Chapter:** 10 · Retrieval-Augmented Generation (RAG) (`exercises/ch10-rag/`) · **Covers:** R10 Retrieval

## Learning objectives
- Implement BM25 scoring and explain every term's contribution.
- Understand how k1 and b control term saturation and length normalization.
- Use keyword search for identifiers that embeddings miss.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch10-rag/ex38-bm25`.
- **Expected output:** all 5 tests fail against the starter; when you're done, all 5 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch10-rag/ex38-bm25`: all 5 pass.
- **Tests:** `test_bm25.py` (5 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** An in-memory index with simple regex tokenization, a fixed English stop-word list and no
  stemming or field weights. In production use a search engine's BM25 (OpenSearch, Elasticsearch, Lucene) with an
  analyzer chosen for the corpus languages, and tune `k1` and `b` against recall on a labeled query set.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "BM25 from scratch". Before I write
code, teach me BM25, inverse document frequency, term-frequency saturation, document length normalisation, and why
exact identifiers need lexical search. Use short Python examples that are not the exercise solution. Then ask me
three questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch10-rag/ex38-bm25/starter.py so that test_bm25.py passes. README.md in that folder is
the spec: follow its names, formats, ordering and error messages exactly. Public API: `BM25`. Constraints: Python
3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do
not modify the tests or fde_kit. When you're done, run `pytest exercises/ch10-rag/ex38-bm25` and show me
the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "BM25 from scratch" as a senior forward deployed engineer would before it ships to a customer.
Specifically: Do explain() contributions sum exactly to score()? Are repeated query terms handled as specified? How
would you tune k1 and b for short FAQ entries versus long policies? Rank findings by customer impact, quote the line
for each, and say which ones a test should catch.
```
