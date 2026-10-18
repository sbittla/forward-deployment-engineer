# ex26 · Bronze / silver / gold mini lakehouse

**Module:** m04 · **Covers:** R04 Data pipelines, R31 Data platforms (Databricks/Snowflake/lakehouse) · **Time:** 60 min

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
