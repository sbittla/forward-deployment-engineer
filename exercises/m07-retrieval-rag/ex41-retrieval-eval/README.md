# ex41 · Retrieval metrics: recall@k, MRR, nDCG

**Module:** m07 · **Covers:** R10 Retrieval, R13 Evaluation · **Time:** 50 min

## Scenario
Your teammate claims the new chunking "feels better". The customer's AI lead asks: *by how much, on what?* Most
RAG failures are retrieval failures, so measure retrieval separately from generation.

## Your task
`qrels = {qid: {"query": str, "relevant": {doc_id: grade}}}` — grade ≥ 1 means relevant (graded for nDCG).

1. `recall_at_k(ranked, relevant, k)` — fraction of relevant docs present in the top k (0.0 if none relevant).
2. `precision_at_k(ranked, relevant, k)` — relevant hits in top k divided by k.
3. `mrr(ranked, relevant)` — 1 / rank of the first relevant doc, 0 if none.
4. `ndcg_at_k(ranked, relevant, k)` — DCG with gain `2**grade - 1` and discount `log2(rank + 1)`, normalised by the
   ideal DCG from sorting grades desc. 0.0 when there are no relevant docs.
5. `evaluate(retrieve, qrels, k) -> dict` — `retrieve(query, k) -> list[doc_id]`. Returns
   `{"per_query": {qid: {...4 metrics}}, "mean": {...}}` with all values rounded to 4 dp.
6. `compare(a, b, names=("A","B")) -> str` — markdown table `| Metric | A | B | Δ |` over the mean metrics in the
   order recall, precision, mrr, ndcg, with Δ formatted with sign (e.g. `+0.1250`).
