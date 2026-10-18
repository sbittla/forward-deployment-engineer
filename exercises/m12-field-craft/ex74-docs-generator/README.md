# ex74 · API reference and quickstart generator

**Module:** m12 · **Covers:** R24 Technical writing & enablement, R01 Python · **Time:** 50 min

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
Implement exercises/m12-field-craft/ex74-docs-generator/starter.py so that test_docs.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `public_api`,
`parse_google_docstring`, `render_reference`, `missing_docs`. Constraints: Python 3.11+, the standard library and
the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit.
When you're done, run `pytest exercises/m12-field-craft/ex74-docs-generator` and show me the output. If the README
and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "API reference and quickstart generator" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Are imported names excluded from the public API? Is __all__ respected exactly?
Are continuation lines in Args parsed correctly? Rank findings by customer impact, quote the line for each, and say
which ones a test should catch.
```
