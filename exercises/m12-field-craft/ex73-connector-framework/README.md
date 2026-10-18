# ex73 · Generalise three customer variants into a config-driven connector

**Module:** m12 · **Covers:** R23 Productisation, R05 Integration, R28 Architecture · **Time:** 60 min

## Learning objectives
- Replace copy-pasted adapters with one config-driven connector engine.
- Support nested paths, transforms and defaults declaratively.
- Validate configs so the next FDE can't ship a broken mapping.

## Scenario
You have written the "CRM → canonical case" adapter three times for three customers, each a slightly different
copy-paste. Product wants it in the platform. Replace the copies with one engine driven by declarative mapping
configs that customers' admins (or the next FDE) can write without code changes.

## Your task
A mapping config:
```python
{"name": "acme", "fields": {
    "case_id":  {"path": "Id", "required": True},
    "subject":  {"path": "Subject", "transforms": ["strip"]},
    "priority": {"path": "Priority__c", "transforms": ["lower", "map:p1=urgent,p2=high,p3=normal"], "default": "normal"},
    "opened":   {"path": "Created.When", "transforms": ["date_iso"]},
    "account":  {"path": "Account.Name"}}}
```
- `path` uses dots for nesting and `[n]` for list indices (`"contacts[0].email"`).
- Built-in transforms: `strip`, `lower`, `upper`, `int`, `date_iso` (accepts ISO dates/datetimes, `MM/DD/YYYY`,
  or epoch seconds → `YYYY-MM-DD`), `map:k=v,...` (unmapped values pass through unchanged).
- `register_transform(name, fn)` adds custom transforms globally.

`Connector.from_config(cfg)` validates the config (raise `ValueError` for missing `name`/`fields`, a field without
`path`, or an unknown transform). `connector.transform(record) -> dict` resolves each field (missing path →
`default` if given, else `None`; required and missing → raise `MappingError(field)`); transforms are skipped for
`None`. `connector.run(records) -> (rows, errors)` collects `(index, field, message)` errors without aborting.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Generalise three customer variants
into a config-driven connector". Before I write code, teach me declarative mapping engines, path expressions,
transform pipelines, plugin registries, and config validation. Use short Python examples that are not the exercise
solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get
one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m12-field-craft/ex73-connector-framework/starter.py so that test_connector.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`MappingError`, `register_transform`, `Connector`. Constraints: Python 3.11+, the standard library and the repo's
fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're
done, run `pytest exercises/m12-field-craft/ex73-connector-framework` and show me the output. If the README and the
tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Generalise three customer variants into a config-driven connector" as a senior forward
deployed engineer would before it ships to a customer. Specifically: Is an unknown transform rejected at config load
rather than at runtime? Do list indices out of range fall back to defaults? Is the global transform registry safe
for tests running in parallel? Rank findings by customer impact, quote the line for each, and say which ones a test
should catch.
```
