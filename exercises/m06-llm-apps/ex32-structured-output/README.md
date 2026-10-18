# ex32 · Structured output with validation and repair

**Module:** m06 · **Covers:** R08 LLM apps, R09 Prompt engineering · **Time:** 60 min

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
