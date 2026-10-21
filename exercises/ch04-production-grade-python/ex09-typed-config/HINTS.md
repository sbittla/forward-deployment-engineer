# ex09 hints · Typed config and secrets loading

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write `Secret` first: a small class that holds the value privately and overrides `__repr__` (and `__str__`) to return
`Secret('****')`. Then make `Settings` a dataclass with the README defaults on the optional fields. `load_settings`
comes last.
</details>

<details>
<summary>Hint 2 · The approach</summary>

Don't raise on the first problem. Start with an empty `errors` list and a dict of parsed values, check each variable,
and append a message that starts with the variable's name whenever a check fails. Only set a value in the dict when
the variable is present and valid, so the dataclass defaults apply to the rest. At the end, raise
`ConfigError(errors)` if the list isn't empty; otherwise build `Settings(**values)`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Wrap each `float(...)` and `int(...)` in `try/except ValueError`, and treat an out-of-range value the same way, so
  `"eleven"` and `"11"` both give one message for `FDE_MAX_RETRIES`.
- A missing variable and an invalid variable each count as **one** error. The bad-env test expects exactly five.
- Python's default dataclass `repr` prints every field, and `api_key` prints as `Secret('****')` only because of
  your `__repr__`. Check this with `repr(settings)`.
- `Secret` equality must compare values, and if you define `__eq__` you should define `__hash__` too.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_happy_path` | Tenants not stripped, or empty entries from `,,` kept; log level not uppercased |
| `test_defaults` | Optional fields have no dataclass defaults, or a missing variable is parsed as `""` |
| `test_all_errors_reported` | Raising on the first error; or two messages for one variable |
| `test_retry_range` | Range check missing (only the int conversion is checked) |
| `test_secret_never_printed` | `Secret` has no `__repr__`, or `redacted()` returns the `Secret` object instead of `"****"` |
