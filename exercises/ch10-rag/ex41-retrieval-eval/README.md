# ex41 · Retrieval metrics: recall@k, MRR, nDCG

**Chapter:** 10 · Retrieval-Augmented Generation (RAG) (`exercises/ch10-rag/`) · **Covers:** R10 Retrieval, R13 Evaluation

## Learning objectives
- Measure retrieval separately from generation.
- Compute recall@k, precision@k, MRR and nDCG correctly.
- Compare two retrieval configurations with a clear delta table.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Retrieval metrics: recall@k, MRR,
nDCG". Before I write code, teach me information-retrieval metrics, graded relevance, ideal DCG, and why most RAG
failures are retrieval failures. Use short Python examples that are not the exercise solution. Then ask me three
questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch10-rag/ex41-retrieval-eval/starter.py so that test_retrieval_eval.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`recall_at_k`, `precision_at_k`, `mrr`, `ndcg_at_k`, `evaluate`, `compare`. Constraints: Python 3.11+, the standard
library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests
or fde_kit. When you're done, run `pytest exercises/ch10-rag/ex41-retrieval-eval` and show me the output.
If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Retrieval metrics: recall@k, MRR, nDCG" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Is nDCG normalised by the ideal ordering of all relevant docs, not just retrieved
ones? Are queries with no relevant docs handled? Is the comparison table sign-formatted correctly? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
