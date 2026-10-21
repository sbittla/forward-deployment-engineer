# ex53 · PII detection and redaction

**Chapter:** 13 · AI Security and Guardrails (`exercises/ch13-ai-security-and-guardrails/`) · **Covers:** R14 Guardrails, R17 Compliance

## Learning objectives
- Detect common PII types with validated patterns (Luhn, SSN rules).
- Replace PII with consistent, restorable tokens before data leaves the VPC.
- Explain the limits of regex detection and how to measure recall.

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

`luhn_ok(digits) -> bool` validates a digit string (separators already removed) with the Luhn
checksum; `detect` uses it for `CREDIT_CARD`.

Only the five types above are detected: names, street addresses and other free text are **not**, so `detect`
returns `[]` for them and `redact` leaves them unchanged (production needs NER; see Field notes).

## Field notes
Regex PII detection is a floor, not a ceiling: names and addresses need NER. Say so in the design review — and log
detector recall on a labelled sample.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch13-ai-security-and-guardrails/ex53-pii-redaction`.
- **Expected output:** all 17 tests fail against the starter; when you're done, all 17 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch13-ai-security-and-guardrails/ex53-pii-redaction`: all 17 pass.
- **Tests:** `test_pii.py` (17 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Regex rules find only structured US-format identifiers: names, addresses and free-text
  descriptions pass through unredacted (`test_boundary_name_not_redacted`). Production adds an NER detector,
  locale-specific rules and a recall figure measured on a labelled sample, and keeps the token mapping in protected
  storage inside the network.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "PII detection and redaction". Before
I write code, teach me PII detection and pseudonymisation, overlapping-match resolution, Luhn validation, and
reversible tokenisation. Use short Python examples that are not the exercise solution. Then ask me three questions
to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch13-ai-security-and-guardrails/ex53-pii-redaction/starter.py so that test_pii.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Entity`, `luhn_ok`,
`detect`, `redact`, `restore`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only
(pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch13-ai-security-and-guardrails/ex53-pii-redaction` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "PII detection and redaction" as a senior forward deployed engineer would before it ships to a
customer. Specifically: Do overlapping detections resolve as specified (earlier, then longer)? Does the same value
always get the same token? Which PII types would leak through, and how would you measure that? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
