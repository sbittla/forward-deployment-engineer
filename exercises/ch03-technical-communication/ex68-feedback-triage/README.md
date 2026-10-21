# ex68 · Field feedback triage to product brief

**Chapter:** 3 · Technical Communication (`exercises/ch03-technical-communication/`) · **Covers:** R23 Product feedback loop, R19 Communication

## Learning objectives
- Cluster field feedback across customers instead of forwarding anecdotes.
- Weigh requests by reach, revenue and severity.
- Write a one-page brief product will act on.

## Scenario
FDEs are the product team's eyes in the field. But a Slack channel of 200 anecdotes isn't feedback — it's noise.
Cluster requests across customers, weigh them by reach and revenue, and write the one-page brief product will act on.

## Your task
Feedback items: `{"customer", "text", "arr" (annual revenue, USD), "severity": "blocker"|"major"|"minor"}`.

1. `cluster(items, threshold=0.3) -> list[list[int]]` — greedy: walk items in order; put each in the first cluster
   whose **first** item's token set (`fde_kit.tokenize`) has Jaccard similarity ≥ `threshold` with it, else start a
   new cluster. Return clusters as lists of item indices.
2. `score(cluster_items) -> float` — `distinct_customers * 10 + total_arr_of_distinct_customers / 100_000 +
   sum(severity weights)` with weights blocker 5, major 2, minor 1 (each customer's ARR counted once). Round 2 dp.
3. `brief(items, top=3, threshold=0.3) -> str` — markdown:
   ```
   # Field feedback brief
   ## 1. <first item text of the cluster>
   - Customers: <n> (<names sorted, comma-separated>)
   - ARR represented: $<total, thousands separators>
   - Severity: <b> blocker, <m> major, <n> minor
   - Score: <score>
   > "<text of the highest-severity item (ties: earliest)>" — <customer>
   ```
   clusters ordered by score desc (ties: earliest first index); one blank line between clusters.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Field feedback triage to product
brief". Before I write code, teach me turning field feedback into product input: clustering, weighting by customers
and ARR, and writing a concise brief with a representative quote. Use short Python examples that are not the
exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read
if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch03-technical-communication/ex68-feedback-triage/starter.py so that test_triage.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `cluster`, `score`,
`brief`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed
where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch03-technical-communication/ex68-feedback-triage` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Field feedback triage to product brief" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Is each customer's ARR counted once per cluster? Does greedy clustering depend on
input order in a way that changes the top item? Would a product manager trust the brief without the raw data? Rank
findings by customer impact, quote the line for each, and say which ones a test should catch.
```
