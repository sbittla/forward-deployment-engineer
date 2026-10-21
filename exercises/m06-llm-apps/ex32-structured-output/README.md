# ex32 · Structured output with validation and repair

**Module:** m06 · **Covers:** R08 LLM apps, R09 Prompt engineering · **Time:** 60 min

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
Implement exercises/m06-llm-apps/ex32-structured-output/starter.py so that test_structured.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `extract_json`,
`validate`, `complete_structured`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package
only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run
`pytest exercises/m06-llm-apps/ex32-structured-output` and show me the output. If the README and the tests disagree,
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
