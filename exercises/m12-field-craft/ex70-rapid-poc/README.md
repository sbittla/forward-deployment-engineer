# ex70 · Time-boxed POC: invoice extraction

**Module:** m12 · **Covers:** R21 Rapid prototyping, R08 LLM apps · **Time-box:** 90 minutes, hard stop

## Scenario
The AP manager at a logistics customer: *"Can AI read our vendor invoices?"* You have until lunch. A good POC is
honest: deterministic rules where they work, the LLM only where they don't, a measured accuracy table on real
samples, and a clear "what it would take" list. Over-engineering a POC is as bad as faking one.

## Your task
Fields: `invoice_number`, `invoice_date` (ISO `YYYY-MM-DD`), `total` (float), `vendor`.

1. `rule_extract(text) -> dict` — regex pass. Return only fields found:
   - number: after `Invoice No`, `Invoice #`, `Invoice Number` or `Inv` (optional `.`/`:`/`#`) → token `[A-Z0-9-]+`
   - date: after `Date` / `Invoice Date`; accept `2026-10-03`, `03/10/2026` (**DD/MM/YYYY**), `Oct 3, 2026`,
     `3 October 2026`
   - total: after `Total`, `Amount Due` or `Balance Due` (not `Subtotal`); currency symbols/codes and thousands
     separators allowed
   - vendor: the first non-empty line, unless it starts with `Invoice`
2. `extract(text, llm=None) -> Extraction(fields, sources)` — rules first; if any field is missing and `llm` is given,
   ask the LLM for the **missing fields only** as JSON (the user message starts with a line
   `Fields: <comma-separated missing field names>`, then a blank line, then the invoice text) and merge (LLM values never override rule values; normalise
   dates/totals the same way). `sources[field]` is `"rule"` or `"llm"`.
3. `evaluate(samples, gold, llm=None) -> dict` — per-field accuracy over samples (4 dp) and `"overall"`, plus
   `"llm_fields"` (count of fields filled by the LLM).
4. `poc_readout(metrics) -> str` — markdown table `| Field | Accuracy |` (one row per field, value as given) and a `## Next steps` list that includes
   `- Improve <field> extraction` for each field under 0.9 accuracy, and always
   `- Run on 200 labelled invoices before any production decision`.
