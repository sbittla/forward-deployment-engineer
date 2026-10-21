# ex43 hints · Tool input validation and error recovery

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write the validator as a function that returns a **list of problems** rather than raising on the first one. The model
fixes its arguments far better when it sees every mistake at once. `dispatch` then becomes a fixed sequence of early
returns: unknown tool, side-effect replay, invalid arguments, exception, success.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- Make the validator recursive over `(schema, value, path)`. A wrong `type` returns one problem straight away.
  Otherwise check enum and min/max, then for objects check required keys, recurse into known properties, and flag
  unknown keys when `additionalProperties` is `False`.
- Build the error content as the heading line plus one `- problem` line per problem.
- Keep a dict of `call_id -> ToolResult` for side-effect tools. Store the result only after a successful call, and
  check the dict before you validate or execute.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The bad-arguments test expects exactly **four** problems: `order_id` missing, `amount` with the wrong type,
  `reason` not in the enum, and `note` not allowed. Make sure a type error on `amount` doesn't also produce a range
  error.
- The exception message must be exactly `Tool <name> failed: <ExceptionType>`. Never include `str(exc)`.
- Truncation keeps the first `max_result_chars` characters and appends `... [truncated N chars]`, where N is the number
  of characters removed.
- `isinstance(True, int)` is True, so number and integer checks must exclude booleans.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_specs` | Specs not in registration order, or the schema key isn't `input_schema` |
| `test_ok` | Result not JSON-encoded |
| `test_invalid_lists_all_problems` | Stopping at the first problem; `fn` called despite invalid arguments |
| `test_range` | `maximum` not checked |
| `test_unknown` | Available tool names not sorted, or the message wording differs |
| `test_exception_sanitised` | Exception message leaked into the result |
| `test_truncation` | Truncation count wrong, or the suffix format differs |
| `test_side_effect_once_per_call_id` | Replay cache keyed by tool name or arguments instead of `call_id` |
| `test_malformed_arguments_rejected` | `args` assumed to be a dict, so a string or `None` crashes instead of failing validation |
| `test_least_privilege_dispatch_as` | Allow by default when `roles` is missing; unknown tool reported as unknown instead of not permitted; `specs_for` lists every tool |
| `test_idempotency_key_runs_once_across_call_ids` | Key checked before validation or ignored; replayed result keeps the first `call_id` |
| `test_audit_entry_per_call_including_denied` | Refused, invalid or replayed calls not logged; `audit_log` returns the internal list instead of a copy |
