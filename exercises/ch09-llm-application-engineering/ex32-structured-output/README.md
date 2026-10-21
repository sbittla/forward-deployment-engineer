# ex32 · Structured output with validation and repair

**Chapter:** 9 · LLM Application Engineering (`exercises/ch09-llm-application-engineering/`) · **Covers:** R08 LLM apps, R09 Prompt engineering

## Learning objectives
- Extract the first complete JSON value from noisy model output.
- Validate against a JSON-Schema subset with precise paths.
- Repair invalid output by feeding validation errors back to the model.

## Scenario
You are extracting claim details from adjuster emails into the customer's claims system. Downstream code expects
exact JSON. Even with a strict prompt, models sometimes wrap JSON in prose, miss a field or use the wrong type.
(Production tip: use the provider's native structured-output / strict tool-schema features when available — but
you still validate at your boundary, because schemas drift and not every deployment target supports them.)

## Your task
1. `extract_json(text) -> dict | list` — find the **first** complete JSON object or array in `text` (may be
   surrounded by prose or ```json fences). Track string literals so braces inside strings don't confuse you.
   Raise `ValueError` if none parses.
2. `validate(obj, schema) -> list[str]` — a JSON-Schema subset: `type` (object, array, string, number, integer,
   boolean, null — `integer` excludes floats and bools, `number` excludes bools), `properties`, `required`,
   `additionalProperties: false`, `enum`, `items`, `minimum`, `maximum`, `minLength`. Return error strings
   prefixed with a JSON path like `$.claimant.name: ...`. Empty list = valid.
3. `complete_structured(llm, prompt, schema, max_repairs=2) -> (obj, attempts)` — ask the model (include the
   schema as JSON in the system prompt), parse + validate; on failure send back the errors and retry up to
   `max_repairs` times. Raise `ValueError` with the last errors if still invalid.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch09-llm-application-engineering/ex32-structured-output`.
- **Expected output:** all 17 tests fail against the starter; when you're done, all 17 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch09-llm-application-engineering/ex32-structured-output`: all 17 pass.
- **Tests:** `test_structured.py` (17 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** `validate` checks shape only, and `complete_structured` reads the reply text without its
  stop reason, so truncated or refused replies spend repairs and schema-valid but invented values pass. In
  production, use the provider's native structured output and a maintained validator such as `jsonschema`, handle
  `max_tokens` and `refusal` separately, and add business-rule and grounding checks (Section 9.2).

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Structured output with validation
and repair". Before I write code, teach me structured output strategies (native schema-constrained output, tool
schemas, prompt-only JSON), boundary validation, and repair loops. Use short Python examples that are not the
exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read
if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch09-llm-application-engineering/ex32-structured-output/starter.py so that test_structured.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `extract_json`,
`validate`, `complete_structured`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package
only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run
`pytest exercises/ch09-llm-application-engineering/ex32-structured-output` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Structured output with validation and repair" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Do braces inside strings or escaped quotes break extraction? Are bools
rejected as integers? Does the repair prompt include the errors and the schema, and is the number of repairs
bounded? Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
**Production prompt (what this exercise's code sends to a model)**
```text
You extract claim details from adjuster emails into the claims system. Return only a JSON object that validates against this JSON Schema:
{schema}

Rules: use null for values the email does not contain; never guess policy numbers or amounts; copy names exactly as written. Do not include prose or code fences.

User turn:
<email>
{email}
</email>
```
