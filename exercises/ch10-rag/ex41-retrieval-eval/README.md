# ex41 · Retrieval metrics: recall@k, MRR, nDCG

**Chapter:** 10 · Retrieval-Augmented Generation (RAG) (`exercises/ch10-rag/`) · **Covers:** R10 Retrieval, R13 Evaluation

## Learning objectives
- Measure retrieval separately from generation.
- Compute recall@k, precision@k, MRR and nDCG correctly.
- Compare two retrieval configurations with a clear delta table.
- Benchmark stale documents, tenant leaks, citation precision and abstention alongside ranking quality.

## Scenario
Your teammate claims the new chunking "feels better". The customer's AI lead asks: *by how much, on what?* Most
RAG failures are retrieval failures, so measure retrieval separately from generation.

## Your task
`qrels = {qid: {"query": str, "relevant": {doc_id: grade}}}` — grade ≥ 1 means relevant (graded for nDCG).

1. `recall_at_k(ranked, relevant, k)` — fraction of relevant docs present in the top k (0.0 if none relevant).
2. `precision_at_k(ranked, relevant, k)` — relevant hits in top k divided by k.
3. `mrr(ranked, relevant)` — 1 / rank of the first relevant doc, 0 if none.
4. `ndcg_at_k(ranked, relevant, k)` — DCG with gain `2**grade - 1` and discount `log2(rank + 1)`, normalized by the
   ideal DCG from sorting grades desc. 0.0 when there are no relevant docs.
5. `evaluate(retrieve, qrels, k) -> dict` — `retrieve(query, k) -> list[doc_id]`. Returns
   `{"per_query": {qid: {...4 metrics}}, "mean": {...}}` with all values rounded to 4 dp.
6. `compare(a, b, names=("A","B")) -> str` — markdown table `| Metric | A | B | Δ |` over the mean metrics in the
   order recall, precision, mrr, ndcg, with Δ formatted with sign (e.g. `+0.1250`).

7. `citation_precision(answers) -> float` — `answers` is a list of `{"citations": [doc_id, ...], "supporting":
   [doc_id, ...]}`. Return supported citations ÷ all citations, pooled over every answer (an answer that cites
   nothing adds nothing), rounded to 4 dp; 0.0 when nothing was cited.
8. `abstention_report(results) -> dict` — `results` is a list of `{"answerable": bool, "abstained": bool}`. Return
   `{"answerable": n, "abstained_answerable": n, "unanswerable": n, "answered_unanswerable": n}`. The launch bar
   for `answered_unanswerable` is zero.
9. `rag_scorecard(results) -> dict` — `results` rows carry all four keys above (`answerable`, `abstained`,
   `citations`, `supporting`). Return `{"citation_precision": citation_precision(results),
   "answered_unanswerable_rate": answered_unanswerable ÷ unanswerable, "abstained_answerable_rate":
   abstained_answerable ÷ answerable}`, the rates from `abstention_report` rounded to 4 dp and `None` when the
   slice is empty. Reporting both rates exposes an assistant that refuses everything.
10. `rewrite_followup(question, history) -> str` — a deterministic stand-in for a model-based query rewrite.
   `history` lists the earlier user questions, oldest first. If `history` is non-empty and the question is a
   follow-up (its stripped, lowercased text starts with `"what about"`, `"how about"`, `"and "` or `"what if"`, or
   one of its words, matched with `[a-z]+`, is `it`, `that`, `this`, `they` or `them`), return
   `f"{history[-1]} {question}"`; otherwise return `question` unchanged. The tests measure it on `FOLLOWUPS`, five
   follow-up questions over the benchmark below with the candidate retriever: recall@3 0.4 → 1.0, MRR 0.2667 → 0.9,
   and one cost: "What about flood?" drops from MRR 1.0 to 0.5 because the burst-pipe terms now outrank it.

### The fixed benchmark in the tests
`test_retrieval_eval.py` ships a small, reproducible benchmark (exercise data) that runs on your functions:
`BENCH_CORPUS` (12 Northwind chunks: two superseded versions, one chunk from tenant `acme`, one upload with no
tenant), `BENCH_QRELS` (8 answerable queries with graded relevance) and `BENCH_UNANSWERABLE` (2 queries). Both
retrievers use the same ranker (the share of query terms found in a chunk, ties by doc id); the **baseline** ranks
every chunk, the **candidate** ranks only current chunks of the user's tenant and drops chunks with no tenant (fail
closed). A question is abstained when the top score is below 0.5; a simulated answer cites its top chunk. The tests
pin the results at k = 3: recall@3 0.9375 → 0.9375, MRR 0.7917 → 1.0, nDCG 0.8235 → 0.9783; queries with a
superseded chunk in the top 3: 6 → 0; with another tenant's or an untenanted chunk: 4 → 0; citation precision
0.625 → 1.0; unanswerable questions answered: 1 of 2 → 0 of 2. Eight queries can't show significance; the point is
that every change to retrieval arrives with these numbers, including the traps.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch10-rag/ex41-retrieval-eval`.
- **Expected output:** all 12 tests fail against the starter; when you're done, all 12 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch10-rag/ex41-retrieval-eval`: all 12 pass.
- **Tests:** `test_retrieval_eval.py` (12 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The metrics are only as good as the qrels: a small hand-labeled set can't show statistical
  significance. In production, build the query set with the customer, version it with the index, include stale,
  conflicting and unanswerable cases, and report retrieval metrics separately from answer-quality metrics.

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
`recall_at_k`, `precision_at_k`, `mrr`, `ndcg_at_k`, `evaluate`, `compare`, `citation_precision`,
`abstention_report`, `rag_scorecard`, `rewrite_followup`. Constraints: Python 3.11+, the standard
library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests
or fde_kit. When you're done, run `pytest exercises/ch10-rag/ex41-retrieval-eval` and show me the output.
If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Retrieval metrics: recall@k, MRR, nDCG" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Is nDCG normalized by the ideal ordering of all relevant docs, not just retrieved
ones? Are queries with no relevant docs handled? Is the comparison table sign-formatted correctly? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
