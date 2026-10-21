# ex31 · Versioned prompt templates

**Chapter:** 9 · LLM Application Engineering (`exercises/ch09-llm-application-engineering/`) · **Covers:** R09 Prompt & context engineering, R08 LLM apps

## Learning objectives
- Treat prompts as versioned, immutable, traceable artifacts.
- Fail loudly on missing or unexpected template variables.
- Join logged answers to the exact prompt version with a content hash.

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Versioned prompt templates". Before
I write code, teach me prompt versioning, semantic versioning, template rendering with strict variables, and prompt
diffs in code review. Use short Python examples that are not the exercise solution. Then ask me three questions to
check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch09-llm-application-engineering/ex31-prompt-templates/starter.py so that test_prompts.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Rendered`,
`PromptRegistry`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is
allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch09-llm-application-engineering/ex31-prompt-templates` and show me the output. If the README and the tests disagree, stop and
tell me instead of guessing.
```
**Review**
```text
Review my solution to "Versioned prompt templates" as a senior forward deployed engineer would before it ships to a
customer. Specifically: Is semver comparison numeric (1.10.0 > 1.9.0)? Does the hash cover the template rather than
the rendered text? How would you roll back a bad prompt version in production? Rank findings by customer impact,
quote the line for each, and say which ones a test should catch.
```
