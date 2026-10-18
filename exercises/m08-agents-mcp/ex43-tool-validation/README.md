# ex43 · Tool input validation and error recovery

**Module:** m08 · **Covers:** R11 Agents & tool use · **Time:** 50 min

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
