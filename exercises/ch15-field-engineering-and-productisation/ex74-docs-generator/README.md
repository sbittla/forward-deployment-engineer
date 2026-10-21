# ex74 · API reference and quickstart generator

**Chapter:** 15 · Field Engineering and Productization (`exercises/ch15-field-engineering-and-productisation/`) · **Covers:** R24 Technical writing & enablement, R01 Python

## Learning objectives
- Generate API reference docs from the code itself.
- Parse Google-style docstrings into structured docs.
- Fail CI when public functions or methods lack docstrings.

## Scenario
The customer's developers will extend your integration after you leave. Hand-written docs drift from the code by
week two. Generate the API reference from the code itself, and fail CI when a public function has no docstring.

## Your task
Work with real module objects (use `inspect`).

1. `public_api(module) -> list[str]` — names of public functions and classes **defined in that module** (not
   imported), not starting with `_`, sorted. If the module defines `__all__`, use exactly that list (sorted).
2. `parse_google_docstring(doc) -> dict` — `{"summary": first paragraph joined into one line, "args": {name: desc},
   "returns": str}` from Google-style `Args:` and `Returns:` sections (argument lines are `name (type): desc` or
   `name: desc`; continuation lines are indented further and appended with a space).
3. `render_reference(module) -> str` — markdown:
   - `# <module name>` then the module docstring's summary
   - for each public item: `## \`name(signature)\``  (classes: `## class \`Name(signature-of-__init__-without-self)\``)
   - the summary; then if args exist, a table `| Argument | Description |`; then `**Returns:** ...` if present
4. `missing_docs(module) -> list[str]` — public items without a docstring, plus public **methods** of public classes
   without one as `Class.method`.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch15-field-engineering-and-productisation/ex74-docs-generator`.
- **Expected output:** all 5 tests fail against the starter; when you're done, all 5 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch15-field-engineering-and-productisation/ex74-docs-generator`: all 5 pass.
- **Tests:** `test_docs.py` (5 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** `inspect` imports the module, so generating the reference runs its top-level code, and only
  Google-style docstrings are parsed. In production, run a maintained documentation generator in CI against a trusted
  build, and keep the hand-written guide that explains concepts and workflows alongside the generated reference.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "API reference and quickstart
generator". Before I write code, teach me docs-as-code, introspection with inspect, Google docstring conventions,
and documentation coverage gates. Use short Python examples that are not the exercise solution. Then ask me three
questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch15-field-engineering-and-productisation/ex74-docs-generator/starter.py so that test_docs.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `public_api`,
`parse_google_docstring`, `render_reference`, `missing_docs`. Constraints: Python 3.11+, the standard library and
the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit.
When you're done, run `pytest exercises/ch15-field-engineering-and-productisation/ex74-docs-generator` and show me the output. If the README
and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "API reference and quickstart generator" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Are imported names excluded from the public API? Is __all__ respected exactly?
Are continuation lines in Args parsed correctly? Rank findings by customer impact, quote the line for each, and say
which ones a test should catch.
```
