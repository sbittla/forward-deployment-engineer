# ex26 · Bronze / silver / gold mini lakehouse

**Module:** m04 · **Covers:** R04 Data pipelines, R31 Data platforms (Databricks/Snowflake/lakehouse) · **Time:** 60 min

## Learning objectives
- Implement bronze, silver and gold layers with clear contracts.
- Quarantine bad records with reasons instead of dropping them.
- Deduplicate deterministically and compute business aggregates.

## Scenario
Databricks, Snowflake and Palantir FDE postings all expect you to think in layered data products. Here you build
the medallion pattern in plain Python so the concepts transfer to Delta Live Tables, dbt or Foundry pipelines:

- **Bronze**: land raw data exactly as received + ingestion metadata. Never drop anything.
- **Silver**: parsed, typed, de-duplicated, conformed. Bad records go to quarantine with a reason.
- **Gold**: business-level aggregates that dashboards and LLM tools query.

## Your task
Input: JSON lines of e-commerce events: `{"event_id","ts","type":"view|purchase","product","country","amount"}`.

1. `bronze(lines, source, ingested_at) -> list[dict]` — one row per line:
   `{"raw": line, "source": source, "ingested_at": ingested_at, "line_no": i}`.
2. `silver(bronze_rows) -> (events, quarantine)`
   - parse JSON; required keys `event_id, ts, type, product, country`; `type` in `{view, purchase}`;
     purchases need numeric `amount >= 0` (views get `amount = 0.0`)
   - normalise `country` to upper-case ISO-2 using `COUNTRY_ALIASES` (e.g. `"usa"`, `"United States"` → `"US"`);
     unknown 2-letter codes are upper-cased; anything else is quarantined
   - de-duplicate by `event_id`, keeping the row with the latest `ts` (ties: latest `line_no`)
   - quarantine rows: `{"line_no", "reason"}`; events sorted by `ts, event_id`; `ts` kept as ISO string
3. `gold(events) -> dict`:
   - `revenue_by_day_country`: `{(YYYY-MM-DD, country): round(sum amount, 2)}` for purchases
   - `conversion_by_product`: `{product: round(purchases / views, 3)}` (products with 0 views omitted)

## Field notes
In Databricks terms: bronze = Auto Loader to a Delta table, silver = `MERGE INTO` with expectations, gold =
materialised views. Keep the quarantine table — it is your best customer-facing data-quality report.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Bronze / silver / gold mini
lakehouse". Before I write code, teach me the medallion architecture, raw data preservation, conforming and
deduplicating events, quarantine tables, and how this maps to Databricks, Snowflake and Foundry pipelines. Use short
Python examples that are not the exercise solution. Then ask me three questions to check my understanding, one at a
time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m04-data-sql/ex26-medallion-pipeline/starter.py so that test_medallion.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `bronze`,
`silver`, `gold`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is
allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m04-data-sql/ex26-medallion-pipeline` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Bronze / silver / gold mini lakehouse" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Is the dedupe tie-break deterministic? Can a malformed line crash silver instead
of being quarantined? Is conversion rate safe when a product has purchases but no views? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
