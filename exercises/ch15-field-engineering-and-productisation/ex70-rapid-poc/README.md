# ex70 · Time-boxed POC: invoice extraction

**Chapter:** 15 · Field Engineering and Productization (`exercises/ch15-field-engineering-and-productisation/`) · **Covers:** R21 Rapid prototyping, R08 LLM apps · **Time-box:** 90 minutes, hard stop

## Learning objectives
- Run an honest, time-boxed POC: rules first, the LLM only for gaps.
- Measure per-field accuracy on real samples.
- Write a readout with clear next steps and limits.

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
   `Fields: <comma-separated missing field names>`, then a blank line, then the invoice text) and merge (LLM values never override rule values; normalize
   dates/totals the same way). `sources[field]` is `"rule"` or `"llm"`.
3. `evaluate(samples, gold, llm=None) -> dict` — per-field accuracy over samples (4 dp) and `"overall"`, plus
   `"llm_fields"` (count of fields filled by the LLM).
4. `poc_readout(metrics) -> str` — markdown table `| Field | Accuracy |` (one row per field, value as given) and a `## Next steps` list that includes
   `- Improve <field> extraction` for each field under 0.9 accuracy, and always
   `- Run on 200 labelled invoices before any production decision`.
5. Injected or malformed model replies change nothing they shouldn't: `extract` merges only the missing `FIELDS`
   (extra keys such as `approved` or `bank_account` are ignored, and rule values are never overridden), and a reply
   whose JSON doesn't parse, or isn't an object, fills nothing.
6. `wilson_lower(p, n, z=1.96) -> float` — the lower end of the Wilson score interval for an accuracy `p` measured on
   `n` samples (`0.0` when `n <= 0`).
7. `exit_decision(metrics, n, gates=EXIT_GATES, min_n=200) -> (decision, reasons)` — the POC's exit gate, applied in
   this order:
   - `n < min_n` → `("extend", ["n=<n> < <min_n> labeled invoices"])`, whatever the accuracy;
   - any field whose accuracy is below its gate → `("no-go", ["<field>: <accuracy> < <gate>", ...])`, in
     `gates` order;
   - any field whose `wilson_lower(accuracy, n)` is below its gate → `("extend", ["<field>: 95% lower bound
     <bound, 3 dp> < <gate>", ...])`;
   - otherwise `("go", [])`.

   `EXIT_GATES = {"invoice_number": 0.95, "invoice_date": 0.95, "total": 0.97, "vendor": 0.90}` (illustrative: agree
   real gates with the accounts-payable manager before the run, not after).

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## From POC to production: the handover pack

Chapter 15's Table 15.1 points here. The readout answers "can it work?"; these tables are what you agree and hand
over when the answer becomes "switch it on". Every target below is *illustrative*: the contract and the customer's
support policy set the real ones.

**Exit gates.** Agree them before the 200-invoice run; `exit_decision` applies the first three.

| Gate | Threshold | Decision if missed |
|---|---|---|
| Sample | At least 200 labeled invoices, held out, drawn across vendors and months | `extend` |
| Accuracy per field | Point estimate at or above `EXIT_GATES` | `no-go` |
| Uncertainty | 95% Wilson lower bound at or above the same gate | `extend` (label more) |
| Cost and latency | Measured cost per successful invoice and p95 latency, with the load model stated, within the agreed budget | `extend` (not tested here) |

**Support model.** Who owns what after handover.

| Tier | Who | Owns | Response target |
|---|---|---|---|
| L1 | The customer's service desk | Intake, known-issue runbook, user communication | Acknowledge within 1 business hour |
| L2 | The customer's platform team (service owner, on call) | Deploy, rollback, kill switch, prompt and configuration changes | Severity 1: respond in 15 minutes, mitigate in 4 hours |
| L3 | Your product engineering team | Defects in shared code, model upgrades, security fixes | Severity 1: engaged within 1 hour |
| Field | You, until the agreed handover date | Shadowing L2 and coaching; no production access afterward | None after handover |

**Ownership-transfer checklist.**

- [ ] A named service owner, and an on-call rotation that has accepted the service and its alerts (Section 14.7).
- [ ] Deploy, rollback, kill-switch and key-rotation runbooks pass the linter and were rehearsed by the owner.
- [ ] Repository, CI, secrets and model keys live in customer-owned accounts; the trial key is revoked.
- [ ] The 200 labeled invoices and the evaluation script are handed over, and the owner has rerun them.
- [ ] Dashboards show per-field accuracy on sampled invoices, cost per invoice and the SLO.
- [ ] Your accounts and tokens are revoked; nothing depends on credentials tied to you.
- [ ] The field-code register (Section 15.6) has an entry with an owner and a review date.

**Product feedback loop.**

| Signal | Goes to | With | When |
|---|---|---|---|
| Field code written for this customer | The field-code register (Section 15.6) | Owner, review date | At handover |
| The same pattern at a second or third customer | The product team, as a feedback brief (Section 3.4) | Golden-output tests, the configuration that varied, incidents, revenue at stake | Monthly |
| A defect in shared code | The product backlog, through L3 | A failing test | Per incident |
| A user's feature request | The feedback brief; close the loop with the requester (Section 3.4) | Number of customers asking | Monthly |

The compliance evidence map (which test or document proves which control) is in ex75's README.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch15-field-engineering-and-productisation/ex70-rapid-poc`.
- **Expected output:** all 9 tests fail against the starter; when you're done, all 9 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch15-field-engineering-and-productisation/ex70-rapid-poc`: all 9 pass.
- **Tests:** `test_poc.py` (9 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Four synthetic invoices and a scripted fake model show feasibility, not accuracy.
  Production needs the 200-invoice labeled evaluation, an owner, runbooks, monitoring, cost limits and a compliance
  review (Chapter 15's POC-to-production table), plus a check on model-filled values before they reach the payment
  system.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Time-boxed POC: invoice extraction".
Before I write code, teach me how to scope a POC, combine deterministic extraction with an LLM fallback, measure
accuracy per field, and present results honestly. Use short Python examples that are not the exercise solution. Then
ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch15-field-engineering-and-productisation/ex70-rapid-poc/starter.py so that test_poc.py passes. README.md in that folder
is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Extraction`,
`rule_extract`, `extract`, `evaluate`, `poc_readout`. Constraints: Python 3.11+, the standard library and the repo's
fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're
done, run `pytest exercises/ch15-field-engineering-and-productisation/ex70-rapid-poc` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Time-boxed POC: invoice extraction" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Can the LLM override a rule-extracted value? Are DD/MM dates parsed as specified
and not as MM/DD? Does the readout state sample size and what was not tested? Rank findings by customer impact,
quote the line for each, and say which ones a test should catch.
```
**Production prompt (what this exercise's code sends to a model)**
```text
Extract the requested fields from the vendor invoice. Return only a JSON object containing exactly the fields listed on the first line, using: invoice_number (string), invoice_date (YYYY-MM-DD), total (number, no currency symbol), vendor (string). Use null when a field is not present; do not guess.

User turn:
Fields: {missing_fields}

{invoice_text}
```
