# ex31 · Versioned prompt templates

**Module:** m06 LLM Applications · **Covers:** R09 Prompt & context engineering, R08 LLM apps · **Time:** 45 min

## Scenario
Three engineers edit the same system prompt in three branches; a regression ships and nobody can say which prompt
produced which answer. Treat prompts like code: named, versioned, validated and traceable in logs.

## Your task
`PromptRegistry`:
- `register(name, version, template)` — `version` is semver `MAJOR.MINOR.PATCH`; template uses `{{var}}`
  placeholders (whitespace inside braces allowed: `{{ var }}`). Re-registering an existing name+version with a
  *different* template raises `ValueError` (immutability); identical re-registration is a no-op.
- `variables(name, version=None) -> set[str]`.
- `render(name, version=None, **vars) -> Rendered` — `version=None` means highest semver (compare numerically:
  `1.10.0 > 1.9.0`). Missing variables → `KeyError` listing **all** missing names; unexpected variables →
  `TypeError`. Values are inserted with `str()`.
- `Rendered(text, name, version, sha)` — `sha` is the first 12 hex chars of SHA-256 of the **template**
  (not the rendered text) so logs can join answers to exact prompt versions.
- `diff(name, v1, v2) -> list[str]` — `difflib.unified_diff` of the two templates' lines (no line endings),
  with `fromfile=f"{name}@{v1}"`, `tofile=f"{name}@{v2}"`.
