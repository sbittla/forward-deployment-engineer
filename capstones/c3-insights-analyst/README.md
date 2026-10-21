# Capstone 3 · Lakehouse ETL + NL-to-SQL analyst (financial services)

**Covers:** R01 Python · R03 SQL & modelling · R04 Pipelines · R05 Integration · R08 LLM apps · R13 Evals ·
R24 Writing · R25 Regulated domain · R31 Data platforms
**Builds on:** ex19, ex22–ex26, ex32, ex49, ex55
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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run
```bash
pytest capstones/c3-insights-analyst
pytest --solutions capstones/c3-insights-analyst
```

## Stretch goals
- Swap SQLite for DuckDB or a Databricks SQL warehouse behind the same `Analyst` interface.
- Add column-level access control (e.g., hide `customer_name` from some roles) enforced in `guard_sql`.
- Add a "show me a chart" mode that returns a Vega-Lite spec built from the result rows.

## Assessment
Assessed with the shared [capstone rubric](../RUBRIC.md): gates first (tests, critical correctness, security and
privacy, honest reporting, plus this capstone's own gates), then a weighted score across nine dimensions. The bar is
every gate passing, a weighted score of at least 3.0 and no dimension below 2. Section 4 of the rubric lists C3's
acceptance criteria and gates. Submit your scorecard as `starter/deliverables/scorecard.md`.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest capstones/c3-insights-analyst`.
- **Expected output:** all 24 tests fail against the starter; when you're done, all 24 pass.
- **Check the reference solution:** `pytest --solutions capstones/c3-insights-analyst`: all 24 pass.
- **Tests:** `tests/test_c3_analyst.py`, `tests/test_c3_deliverables.py`, `tests/test_c3_etl_semantic.py`,
  `tests/test_c3_sqlguard.py` (24 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The SQL guard parses text and the model attempts are scripted. Production also connects
  with a read-only database role limited to the allow-listed tables, sets statement timeouts and row limits in the
  database, and runs the unsafe-query evals against every model or prompt change.

