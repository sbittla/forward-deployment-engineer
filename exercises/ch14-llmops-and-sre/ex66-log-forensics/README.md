# ex66 · Log forensics: root-cause an incident

**Chapter:** 14 · LLMOps and SRE (`exercises/ch14-llmops-and-sre/`) · **Covers:** R29 Debugging in customer environments, R15 Observability

## Learning objectives
- Parse multi-service logs and compute error rates over time.
- Find the root-cause service using the dependency graph.
- Write an incident summary that ends the blame game.

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

When no service logged an ERROR, `root_cause` returns `None` and the summary says `Root cause: none` and `Blast radius: none`.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch14-llmops-and-sre/ex66-log-forensics`.
- **Expected output:** all 6 tests fail against the starter; when you're done, all 6 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch14-llmops-and-sre/ex66-log-forensics`: all 6
  pass.
- **Tests:** `test_forensics.py` (6 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The root cause comes from first-error timestamps and a declared dependency map, which
  assumes synchronized clocks and complete logs. Treat it as the first hypothesis: confirm it with traces, metrics
  and change records, and allow for causes outside the logs, such as network or certificate changes.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Log forensics: root-cause an
incident". Before I write code, teach me log forensics, correlating events across services, dependency-aware
root-cause analysis, and blast radius. Use short Python examples that are not the exercise solution. Then ask me
three questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch14-llmops-and-sre/ex66-log-forensics/starter.py so that test_forensics.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `parse`,
`error_rate_by_minute`, `first_errors`, `root_cause`, `timeline`, `incident_summary`. Constraints: Python 3.11+, the
standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify
the tests or fde_kit. When you're done, run `pytest exercises/ch14-llmops-and-sre/ex66-log-forensics` and show me the
output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Log forensics: root-cause an incident" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Are malformed lines counted and skipped without crashing? Is transitive
dependency traversal safe from cycles? Could clock skew between services mislead the root-cause logic? Rank findings
by customer impact, quote the line for each, and say which ones a test should catch.
```
