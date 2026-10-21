# ex38 · BM25 from scratch

**Module:** m07 · **Covers:** R10 Retrieval · **Time:** 45 min

## Learning objectives
- Implement BM25 scoring and explain every term's contribution.
- Understand how k1 and b control term saturation and length normalisation.
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
Implement exercises/m07-retrieval-rag/ex38-bm25/starter.py so that test_bm25.py passes. README.md in that folder is
the spec: follow its names, formats, ordering and error messages exactly. Public API: `BM25`. Constraints: Python
3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do
not modify the tests or fde_kit. When you're done, run `pytest exercises/m07-retrieval-rag/ex38-bm25` and show me
the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "BM25 from scratch" as a senior forward deployed engineer would before it ships to a customer.
Specifically: Do explain() contributions sum exactly to score()? Are repeated query terms handled as specified? How
would you tune k1 and b for short FAQ entries versus long policies? Rank findings by customer impact, quote the line
for each, and say which ones a test should catch.
```
