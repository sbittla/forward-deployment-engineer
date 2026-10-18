# ex68 · Field feedback triage to product brief

**Module:** m12 · **Covers:** R23 Product feedback loop, R19 Communication · **Time:** 50 min

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
