# Capstone 3 · Lakehouse ETL + NL-to-SQL analyst (financial services)

**Covers:** R01 Python · R03 SQL & modelling · R04 Pipelines · R05 Integration · R08 LLM apps · R13 Evals ·
R24 Writing · R25 Regulated domain · R31 Data platforms
**Suggested time:** 2 days · **Builds on:** ex19, ex22–ex26, ex32, ex49, ex55
**Take after:** End of Part III: after ex32, ex49 and ex55, plus ex19 and ex22–ex26 from Part II.

## The engagement
A commercial bank wants relationship managers to ask questions like "Which client spent the most in Q1?" without
filing a ticket with the analytics team. The Chief Data Officer's conditions:
1. data lands through a governed pipeline with data-quality checks and a quarantine, not ad-hoc CSV imports
2. the assistant can never change data, reach system tables or other databases, or invent numbers
3. every answer shows its SQL, and accuracy is measured against analyst-written gold queries

Data in `data/`: an `accounts.csv`, a deliberately messy `transactions.csv` (mixed date formats, thousands
separators, SEK amounts, a duplicate with a later correction, an unknown account, a missing date, a non-numeric
amount), and `questions.json`: 7 questions with gold SQL and **scripted model attempts**, some wrong and some
malicious.

## What you build (`starter/insights/`)
| Module | Responsibility |
|---|---|
| `etl.py` | `load_warehouse()`: bronze rows → silver (typed, FX to USD, latest `updated_at` wins, referential checks) → gold `monthly_spend` view; `LoadReport` with quarantine reasons |
| `semantic.py` | Metric definitions, the schema prompt, a generated data dictionary |
| `sqlguard.py` | `guard_sql()`: single statement, SELECT/WITH only, forbidden keywords, table allow-list (CTEs allowed), row-limit enforcement, comment stripping |
| `analyst.py` | NL→SQL with a repair loop (errors are fed back to the model), `CANNOT_ANSWER` handling, refusal after N attempts, narratives computed from the result |
| `evals.py` | Execution accuracy vs gold result sets (order-aware only when the gold SQL orders), refusal accuracy, unsafe-blocked count |

## Deliverables (`starter/deliverables/`)
- `analyst_guide.md`: for relationship managers: how to ask, what it won't do, metric definitions, freshness,
  escalation.
- `exec_readout.md`: measured results (percentages), controls, risks, next steps. Quote **your** eval numbers.

## Run
```bash
pytest capstones/c3-insights-analyst
pytest --solutions capstones/c3-insights-analyst
```

## Stretch goals
- Swap SQLite for DuckDB or a Databricks SQL warehouse behind the same `Analyst` interface.
- Add column-level access control (e.g., hide `customer_name` from some roles) enforced in `guard_sql`.
- Add a "show me a chart" mode that returns a Vega-Lite spec built from the result rows.
