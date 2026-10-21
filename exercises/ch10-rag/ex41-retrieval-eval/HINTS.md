# ex41 hints · Retrieval metrics: recall@k, MRR, nDCG

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Treat "relevant" as "grade ≥ 1" everywhere, and write the four metric functions as small, separate functions. Check
each against the numbers in the tests before you write `evaluate`, which only loops over queries and averages.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **recall@k:** relevant docs found in `ranked[:k]` divided by the total number of relevant docs.
- **precision@k:** relevant docs in `ranked[:k]` divided by **k** (not by the list length).
- **MRR:** walk the ranking with `enumerate(ranked, 1)` and return `1 / rank` at the first relevant doc.
- **nDCG:** a `_dcg(grades)` helper with gain `2**g - 1` and discount `log2(rank + 1)`. Compute it once for the
  ranking's grades (0 for unjudged docs) and once for the ideal ranking: all grades sorted descending, cut to k.
- **compare:** use `f"{value:.4f}"` for values and `f"{delta:+.4f}"` for the signed delta.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Every metric returns 0.0 when there are no relevant docs. Guard each division, especially the ideal DCG.
- Cut the ideal grades to **k** too, or nDCG can never reach 1.0 when there are more relevant docs than k.
- The discount for rank 1 is `log2(2) = 1`, so ranks start at 1.
- Round per-query values to 4 dp, then average the rounded values and round the mean again.
- The Δ column is `B - A` (second minus first).
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_recall_precision` | Precision divided by the number of results instead of k |
| `test_mrr` | 0-based rank (`1/2` instead of `1/3`) |
| `test_ndcg` | Linear gain instead of `2**g - 1`; ideal not sorted descending; discount off by one |
| `test_evaluate_and_compare` | Delta sign reversed; metric rows in the wrong order; values not formatted to 4 dp |
| `test_no_relevant_documents` | Division by zero when nothing is relevant or the ranking is empty |
| `test_citation_precision_and_abstention_report` | Precision averaged per answer instead of pooled over all citations; an answer with no citations counted as 0 or 1 |
| `test_benchmark_baseline_vs_candidate` | One of the four metrics is off; check the unit tests above first, since the benchmark only reuses them |
| `test_benchmark_stale_and_foreign_never_cited` | `citation_precision` not pooled or not rounded to 4 dp |
| `test_benchmark_abstention` | `answered_unanswerable` counts abstentions instead of answers, or the keys differ |
| `test_rag_scorecard` | A rate computed over all cases instead of its own slice; 0 instead of `None` for an empty slice; rates not rounded to 4 dp |
| `test_rewrite_followup` | Prefix checked case-sensitively, or a standalone question rewritten; empty history not handled |
| `test_rewrite_followup_recall` | Previous question placed after the follow-up or the wrong history entry used; check `test_rewrite_followup` first |
