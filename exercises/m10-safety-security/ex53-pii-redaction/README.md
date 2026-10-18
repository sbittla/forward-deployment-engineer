# ex53 · PII detection and redaction

**Module:** m10 Safety, Security & Compliance · **Covers:** R14 Guardrails, R17 Compliance · **Time:** 60 min

## Scenario
Before any transcript leaves the customer's VPC for an LLM API, their privacy office requires PII to be replaced
with tokens — consistently, so the model can still reason ("[EMAIL_1] emailed twice") — and restorable inside the VPC
for the final answer.

## Your task
`detect(text) -> list[Entity(type, start, end, value)]`, sorted by `start`, non-overlapping (earlier/longer wins):

| type | rule |
|---|---|
| `EMAIL` | `local@domain.tld` |
| `SSN` | `###-##-####`, area not `000`, `666` or `9xx`; group not `00`; serial not `0000` |
| `CREDIT_CARD` | 13–19 digits, optionally separated by single spaces or dashes, **passing the Luhn check** |
| `PHONE` | US: optional `+1`/`1`, then `(415) 555-0100`, `415-555-0100`, `415.555.0100`, `415 555 0100` |
| `IP` | IPv4 with each octet 0–255 |

`redact(text, mode="token") -> (redacted, mapping)`:
- `mode="mask"` → `[EMAIL]`, `[PHONE]`… and an empty mapping
- `mode="token"` → `[EMAIL_1]`, `[EMAIL_2]`… numbered per type in order of first appearance; the **same value
  always gets the same token**; `mapping = {token: original}`
`restore(text, mapping)` puts originals back.

## Field notes
Regex PII detection is a floor, not a ceiling: names and addresses need NER. Say so in the design review — and log
detector recall on a labelled sample.
