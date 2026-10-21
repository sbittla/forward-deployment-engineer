# ex38 hints · BM25 from scratch

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

In `fit`, precompute everything the formula needs: a `Counter` of term frequencies per document, each document's
length in tokens, the average length, `N`, and document frequency (the number of docs containing each term). Use
`fde_kit.tokenize` for both documents and queries, so stopwords are dropped the same way on both sides.
</details>

<details>
<summary>Hint 2 · The approach</summary>

Write a `_term(term, doc_id)` helper that returns one term's contribution (0 if the doc doesn't contain it). Then
`explain` loops over the query tokens and adds each token's contribution to a dict entry, and `score` is the sum of
`explain`'s values. Because `score` is defined through `explain`, the "sums to score" test passes automatically.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Document frequency counts each document **once** per term, however many times the term appears in it. Build it from
  the per-doc counters' keys.
- A repeated query term contributes once per occurrence, so in `explain` *add* to the dict entry rather than
  overwriting it.
- Search keeps only scores above 0 and sorts by `(-score, doc_id)`, so equal scores come out in id order.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_idf` | `df` counts occurrences instead of documents; natural log replaced by `log10` |
| `test_exact_score` | Document length counted before stopword removal; `avgdl` computed over raw text |
| `test_search_ranking` | Zero-score docs included |
| `test_explain_sums` | `explain` and `score` computed separately and disagree |
| `test_k_and_ties` | Ties broken by insertion order instead of doc id |
