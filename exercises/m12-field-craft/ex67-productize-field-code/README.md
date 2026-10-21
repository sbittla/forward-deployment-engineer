# ex67 · Productise a one-off field script

**Module:** m12 Field Craft · **Covers:** R23 Product feedback loop & reusable code · **Time:** 50 min

## Learning objectives
- Turn a one-off customer script into configurable product code.
- Prove behaviour is unchanged with a golden-output comparison.
- Remove customer names and constants from library code.

## Scenario
Six months ago you wrote `legacy_acme_report()` on site at Acme in an afternoon. Now Globex wants the same thing,
and product asks whether it can become a feature. The script is full of Acme-specific constants. Productise it:
same behaviour for Acme via configuration, works for Globex, no customer names in library code.

## Your task
Keep `legacy_acme_report` untouched (it's the reference). Implement:
- `ReportConfig(customer_name, sla_hours: dict[priority, hours], priority_aliases: dict[str, str], utc_offset_hours,
  escalation_contact)` with `validate()` raising `ValueError` if any canonical priority in `priority_aliases.values()`
  lacks an SLA, or SLAs are not positive.
- `build_report(tickets, config, now) -> str` that reproduces the legacy output **exactly** for
  `ACME_CONFIG` and works for any other config. Tickets: `{"id", "priority", "opened" (ISO, UTC)}`; priorities are
  mapped through `priority_aliases` (case-insensitive); unknown priorities count as `"normal"`.
- `ACME_CONFIG` — the configuration that reproduces the legacy report.

`build_report`'s source must not mention any customer by name.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Productise a one-off field script".
Before I write code, teach me productising field code: extracting configuration, characterisation tests that pin
legacy behaviour, and validating configs. Use short Python examples that are not the exercise solution. Then ask me
three questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m12-field-craft/ex67-productize-field-code/starter.py so that test_productize.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`legacy_acme_report`, `ReportConfig`, `build_report`. Constraints: Python 3.11+, the standard library and the repo's
fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're
done, run `pytest exercises/m12-field-craft/ex67-productize-field-code` and show me the output. If the README and
the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Productise a one-off field script" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Does build_report reproduce the legacy output byte for byte, including ordering
and time zones? Is config validation strict enough to catch a missing SLA? What would product need before shipping
this? Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
