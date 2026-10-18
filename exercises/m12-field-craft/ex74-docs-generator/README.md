# ex74 · API reference and quickstart generator

**Module:** m12 · **Covers:** R24 Technical writing & enablement, R01 Python · **Time:** 50 min

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
