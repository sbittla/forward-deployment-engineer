# ex63 hints · Customer-environment preflight checker

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Every factory has the same shape: define an inner `fn()` that returns `(ok, detail)` and wrap it in
`Check(name, fn, severity, hint)`. Write `env_vars` and `python_version` first. The rendered names include the target
(`disk_free(/)`, `dns(host)`, `tcp(host:port)`), so check them against the test strings.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- Network and DNS checks catch any exception and report `type(exc).__name__` as the detail. On site, the exception
  *type* (`gaierror`, `ConnectionRefusedError`) tells IT what's wrong.
- `run_preflight` runs every check inside its own `try/except`, so one crashing check doesn't stop the others.
- `Report.status`: any failed check with severity `fail` gives FAIL; otherwise any failed check gives WARN; otherwise
  PASS. `exit_code` maps those to 0, 1 and 2.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The render label for a failed check is its **severity** in upper case, so a failed warn-level check prints
  `[WARN]`, not `[FAIL]`.
- `clock_skew` defaults to severity `warn`, while the other checks default to `fail`.
- Show the hint only when the check failed and the hint isn't empty.
- `writable` should actually create and delete a temporary file (`tempfile.mkstemp(dir=path)`). A missing directory
  then raises, and `run_preflight` turns that into a failure.
- Disk detail: `f"{free_gb:.1f} GB free"` with `free / 1e9`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_all_pass` | Check name or detail format differs (`disk_free(/) — 90.0 GB free`); em dash replaced by a hyphen |
| `test_failures_and_hints` | Version detail not `3.9.7 < 3.11`; hint shown for passing checks; failed warn check labeled FAIL |
| `test_warn_only` | `clock_skew` defaults to severity `fail` |
| `test_crashing_check` | An exception from `fn` escapes `run_preflight` |
| `test_not_writable` | `writable` only checks `os.access`, or swallows the error and reports success |
