# ex67 · Productise a one-off field script

**Module:** m12 Field Craft · **Covers:** R23 Product feedback loop & reusable code · **Time:** 50 min

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
