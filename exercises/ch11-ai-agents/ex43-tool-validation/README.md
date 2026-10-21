# ex43 · Tool input validation and error recovery

**Chapter:** 11 · AI Agents (`exercises/ch11-ai-agents/`) · **Covers:** R11 Agents & tool use

## Learning objectives
- Validate tool arguments before execution and return actionable errors.
- Hide internals (tracebacks, messages) from tool error text.
- Make side-effecting tools idempotent per call id.

## Scenario
In production the model occasionally calls `issue_refund` with `amount: "50 dollars"` or forgets `order_id`. If
your tool crashes with a stack trace, the agent spirals. If it returns a clear, actionable error, the model fixes
its call on the next turn. Side-effecting tools must also be safe against duplicate calls.

## Your task
`ToolRegistry(max_result_chars=2000)`:
- `register(name, description, schema, fn, side_effect=False)`
- `specs()` → list of `{"name", "description", "input_schema"}`
- `dispatch(call_id, name, args) -> ToolResult(call_id, content, is_error)`:
  1. unknown tool → error `"Unknown tool '<name>'. Available: a, b"` (sorted names)
  2. validate `args` against the schema (support `type` object/string/number/integer/boolean/array, `required`,
     `properties`, `enum`, `minimum`, `maximum`, `additionalProperties: false`). On failure return an error whose
     content starts with `"Invalid arguments for <name>:"` followed by one `- <problem>` line per problem — and do
     **not** call `fn`.
  3. `fn(**args)` raising → error `"Tool <name> failed: <ExceptionType>"` (no message, no traceback — they can leak
     internals).
  4. results are JSON-encoded unless strings; longer than `max_result_chars` → truncate and append
     `"... [truncated N chars]"`.
  5. `side_effect=True` tools are executed at most once per `call_id`: a repeated `call_id` returns the first
     result without calling `fn` again.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Tool input validation and error
recovery". Before I write code, teach me schema validation for tool inputs, error messages that let a model
self-correct, result truncation, and idempotency for side effects. Use short Python examples that are not the
exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read
if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch11-ai-agents/ex43-tool-validation/starter.py so that test_tools.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `ToolResult`,
`ToolRegistry`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is
allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch11-ai-agents/ex43-tool-validation` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Tool input validation and error recovery" as a senior forward deployed engineer would before
it ships to a customer. Specifically: Is every validation problem listed, one per line? Could a tool error leak a
database message? Is the side-effect cache keyed by call id only, and should it include arguments? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
