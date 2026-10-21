# ex73 hints · Generalize three customer variants into a config-driven connector

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write the path resolver first. A regex like `([^.\[\]]+)|\[(\d+)\]` splits `org.contacts[0].company` into keys and
indices. Walk the record with them, and return a sentinel object (not `None`) when any step fails, so you can tell
"missing" apart from "present but null" if you need to.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- Keep a module-level dict `TRANSFORMS` of name to function, with `register_transform` adding to it.
- `map:k=v,...` isn't in the dict. Parse it into a lookup table when the config loads, and return `table.get(v, v)`,
  so unmapped values pass through.
- `from_config` validates everything up front: name, fields, a path on every field, and every transform known.
  Building each field's pipeline there means unknown transforms fail at load time, not on the first record.
- `transform` resolves each field; if it's missing, raise for required fields or use the default; otherwise run the
  pipeline.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `date_iso` must accept three shapes: epoch seconds (an int, or a string of digits) using UTC, `MM/DD/YYYY`, and ISO
  with a trailing `Z`. Older Pythons' `fromisoformat` rejects `Z`, so replace it with `+00:00`.
- Look transforms up **late** (at call time), so a transform registered after `from_config` is still used.
- Defaults skip the transforms: a missing priority becomes `"normal"` as written.
- `run` turns `MappingError` into `(index, field, "required field missing")` and keeps going.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_three_customers_same_canonical_output` | List index in the path not supported; epoch not converted in UTC; `"1"` not turned into an int before the custom transform |
| `test_defaults_and_passthrough` | Unmapped values become `None` instead of passing through; default not used for a missing path |
| `test_run_collects_errors` | One bad record aborts the run; error tuple format differs |
| `test_config_validation` | Unknown transforms only detected on the first record, or a missing `path` accepted |
