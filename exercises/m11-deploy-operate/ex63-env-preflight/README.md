# ex63 · Customer-environment preflight checker

**Module:** m11 · **Covers:** R26 On-site embedding, R29 Troubleshooting, R06 Cloud environments · **Time:** 50 min

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
