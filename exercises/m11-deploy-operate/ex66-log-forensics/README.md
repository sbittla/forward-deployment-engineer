# ex66 · Log forensics: root-cause an incident

**Module:** m11 · **Covers:** R29 Debugging in customer environments, R15 Observability · **Time:** 60 min

## Scenario
Saturday 02:14: the customer's gateway started returning 502s on the copilot. By the time you joined the bridge,
everything had recovered and three teams were blaming each other. You have the JSON logs from `gateway`, `api`,
`retriever` and `vectordb`, and the dependency map. Find what broke first.

## Your task
Log lines are JSON: `{"ts": ISO-8601, "service", "level": "INFO"|"WARN"|"ERROR", "msg", "request_id"?}`.
Malformed lines are counted and skipped.

1. `parse(lines) -> (records, bad_count)` — records sorted by `ts` (keep original order for ties).
2. `error_rate_by_minute(records) -> {service: {"HH:MM": rate}}` — ERROR share per service per minute (3 dp).
3. `first_errors(records) -> {service: ts}` — first ERROR timestamp per service.
4. `root_cause(records, deps) -> str` — `deps = {service: [services it calls]}`. Among services with errors, the
   root cause is the one whose own dependencies (transitively) had **no errors before its first error**; if several
   qualify, pick the earliest first error.
5. `timeline(records, request_id) -> list[str]` — `"<ts> <service> <level> <msg>"` for that request in time order.
6. `incident_summary(lines, deps) -> str` — markdown: `# Incident summary`, `Root cause: <service>`,
   `Blast radius: a, b, c` (services with errors, ordered by first error), `Malformed lines: N`.
