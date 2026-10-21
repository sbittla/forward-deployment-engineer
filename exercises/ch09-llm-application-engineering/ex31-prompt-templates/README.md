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
  `TypeError`. Values are inserted with `str()` in a single pass, so a value containing `{{language}}` stays
  literal text and can't pull in another variable.
- `Rendered(text, name, version, sha)` — `sha` is the first 12 hex chars of SHA-256 of the **template**
  (not the rendered text) so logs can join answers to exact prompt versions, and a log line of name, version and
  sha carries no user data.
- `diff(name, v1, v2) -> list[str]` — `difflib.unified_diff` of the two templates' lines (no line endings),
  with `fromfile=f"{name}@{v1}"`, `tofile=f"{name}@{v2}"`.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch09-llm-application-engineering/ex31-prompt-templates`.
- **Expected output:** all 8 tests fail against the starter; when you're done, all 8 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch09-llm-application-engineering/ex31-prompt-templates`: all 8 pass.
- **Tests:** `test_prompts.py` (8 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The registry lives in memory and the hash covers only the template text. A production
  registry is a reviewed, version-controlled store with access control, and the logged hash should be joined with the
  model, its parameters and the retrieval configuration, because those change answers too.

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
