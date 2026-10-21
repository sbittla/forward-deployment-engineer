# ex67 · Productise a one-off field script

**Chapter:** 15 · Field Engineering and Productisation (`exercises/ch15-field-engineering-and-productisation/`) · **Covers:** R23 Product feedback loop & reusable code

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

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch15-field-engineering-and-productisation/ex67-productize-field-code`.
- **Expected output:** 3 of the 4 tests fail against the starter (the one that passes checks scaffolding the starter
  already provides); when you're done, all 4 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch15-field-engineering-and-productisation/ex67-productize-field-code`: all 4 pass.
- **Tests:** `test_productize.py` (4 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The golden-output test compares a small ticket fixture with the legacy script, the name
  check looks only for Acme in `build_report`, and a fixed UTC offset ignores daylight saving. In production, pin the
  original customer's output on a large sample of real tickets, including time-zone edges, and keep each customer's
  configuration under version control with review.

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
Implement exercises/ch15-field-engineering-and-productisation/ex67-productize-field-code/starter.py so that test_productize.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`legacy_acme_report`, `ReportConfig`, `build_report`. Constraints: Python 3.11+, the standard library and the repo's
fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're
done, run `pytest exercises/ch15-field-engineering-and-productisation/ex67-productize-field-code` and show me the output. If the README and
the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Productise a one-off field script" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Does build_report reproduce the legacy output byte for byte, including ordering
and time zones? Is config validation strict enough to catch a missing SLA? What would product need before shipping
this? Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
