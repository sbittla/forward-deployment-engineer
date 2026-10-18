# ex63 · Customer-environment preflight checker

**Module:** m11 · **Covers:** R26 On-site embedding, R29 Troubleshooting, R06 Cloud environments · **Time:** 50 min

## Learning objectives
- Ship a preflight script the customer's IT team runs before you arrive.
- Check Python, env vars, disk, DNS, TCP, clock skew and write access.
- Report clear pass/warn/fail status with actionable hints.

## Scenario
Your first day on site always loses hours to the same problems: wrong Python, missing env vars, DNS that can't
resolve the model endpoint, a firewall blocking 443, a full disk, a skewed clock that breaks TLS and OAuth. Ship a
preflight script the customer's IT team runs *before* you arrive and sends you the output.

## Your task
`Check(name, fn, severity="fail", hint="")` where `fn() -> (ok: bool, detail: str)`.
Factories (all accept `severity` and `hint` keywords):
- `python_version(min_version: tuple, current=sys.version_info[:3])`
- `env_vars(names, env)` — detail lists missing names (`"missing: A, B"`) or `"all set"`
- `disk_free(path, min_gb, usage=shutil.disk_usage)` — detail `"<x.x> GB free"`
- `dns(host, resolve=socket.gethostbyname)` — any exception → not ok, detail = exception type name
- `tcp(host, port, connect)` — `connect(host, port)` returns None or raises; detail `"connected"` or the error type
- `clock_skew(reference_epoch, max_skew_s=60, now=time.time)` — detail `"skew <n>s"` (integer seconds)
- `writable(path)` — tries to create and delete a temp file in `path`

`run_preflight(checks) -> Report` — runs every check (a check whose `fn` raises counts as failed with the
exception type as detail). `Report.status`: `"FAIL"` if any failed check has severity `fail`, else `"WARN"` if any
failed check has severity `warn`, else `"PASS"`. `Report.render()` → one line per check:
`[PASS] name — detail` / `[FAIL] name — detail (hint: ...)` (hint only when failing and non-empty), then a final
line `Overall: PASS|WARN|FAIL`. `Report.exit_code` → 0 PASS, 1 WARN, 2 FAIL.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Customer-environment preflight
checker". Before I write code, teach me the environment problems that derail on-site days (proxy, DNS, firewall,
disk, clock skew) and how to detect them automatically. Use short Python examples that are not the exercise
solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get
one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m11-deploy-operate/ex63-env-preflight/starter.py so that test_preflight.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Check`,
`Report`, `python_version`, `env_vars`, `disk_free`, `dns`, `tcp`, `clock_skew`, `writable`, `run_preflight`.
Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the
README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m11-deploy-operate/ex63-env-preflight` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Customer-environment preflight checker" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Can one check that raises stop the others? Are hints shown only on failure? Would
a customer's IT team understand the output without you on the call? Rank findings by customer impact, quote the line
for each, and say which ones a test should catch.
```
