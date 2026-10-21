# ex32 hints · Structured output with validation and repair

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Do the three functions in order; each one only needs the one before it. For `extract_json`, separate the two jobs:
first find candidate spans that *look* balanced, then try `json.loads` on each in turn and return the first that
parses.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Candidates:** from every `{` or `[`, scan forward keeping a depth counter, and stop when the depth returns to
  zero. Track whether you're inside a string literal (a `"` toggles it, and `\` escapes the next character), and
  ignore brackets while inside one.
- **validate:** make it recursive with a `path` argument. Check the type first; if it's wrong, return that single
  error, because further checks would be noise. Then check enum, min/max, minLength, required keys, then recurse
  into properties (`path.key`) and items (`path[i]`).
- **Repair loop:** at most `max_repairs + 1` model calls. After a failure, append the reply and a user message listing
  the errors.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `isinstance(True, int)` is True. Both `integer` and `number` must exclude booleans, and `integer` must also exclude
  floats.
- `bad {not json} then {"ok": true}`: the first balanced span fails to parse, so keep going rather than giving up.
- `additionalProperties: false` errors must mention the key's name.
- Put the schema in the **system** prompt as JSON (the test looks for `"claim_id"` there). The repair message must
  quote the error paths (it looks for `$.amount`).
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_extract_from_prose_and_fences` | A `}` inside a string ends the span; stopping after the first failed candidate |
| `test_validate_ok` | Optional properties treated as required |
| `test_validate_errors` | Booleans accepted as numbers; floats accepted as integers; array item paths not `[i]` |
| `test_missing_required` | Required check skipped when other properties are present |
| `test_repair_loop` | Schema not in the system prompt; repair message lacks the error paths |
| `test_gives_up` | Wrong number of calls (should be `max_repairs + 1`), or final error doesn't list the problems |
