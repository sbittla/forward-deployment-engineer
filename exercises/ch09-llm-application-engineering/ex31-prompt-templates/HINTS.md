# ex31 hints · Versioned prompt templates

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write one compiled regex for a placeholder, `\{\{\s*(name)\s*\}\}`, where the name is a Python-style identifier. Almost
everything uses it: `findall` gives the variables and `sub` with a function does the rendering. Store templates as
`name -> {version -> template}`.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- Turn `"1.10.0"` into the tuple `(1, 10, 0)` with a small helper. Then `max(versions, key=helper)` finds the latest
  version, and tuples compare numerically.
- In `render`, compute the needed variables once with set arithmetic: `needed - given` is the missing set, and
  `given - needed` is the unexpected set. Raise for missing first, listing every name.
- `sha` hashes the **template**, so two renders of the same version share it whatever the values.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Comparing version strings directly puts `"1.9.0"` after `"1.10.0"`. Always compare the parsed tuples.
- Re-registering the same template is allowed; a *different* template under an existing version raises
  `ValueError`. Check before you overwrite.
- For `diff`, use `splitlines()` (no line endings) and pass `lineterm=""` to `difflib.unified_diff`, or the header
  lines end with `\n` and won't equal `--- claims@1.0.0`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_latest_is_semver` | Versions compared as strings, so 1.9.0 wins |
| `test_render_specific` | `{{ language }}` with spaces not matched; sha computed from the rendered text |
| `test_variables` | Default version not resolved to the latest in `variables` |
| `test_missing_and_unexpected` | Only the first missing name reported; unexpected variables silently ignored |
| `test_immutability` | Identical re-registration raises, or a changed template overwrites silently |
| `test_diff` | Header lines carry trailing newlines (missing `lineterm=""`) |
| `test_value_cannot_inject_template_variables` | Substitution repeated until no placeholders remain, so a value can expand another variable |
| `test_log_fields_carry_no_user_data` | `sha` computed over the rendered text, which changes per request and embeds user data |
