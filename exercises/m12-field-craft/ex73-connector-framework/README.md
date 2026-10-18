# ex73 · Generalise three customer variants into a config-driven connector

**Module:** m12 · **Covers:** R23 Productisation, R05 Integration, R28 Architecture · **Time:** 60 min

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
