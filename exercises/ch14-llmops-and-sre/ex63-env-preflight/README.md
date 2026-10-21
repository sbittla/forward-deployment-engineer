# ex63 · Customer-environment preflight checker

**Chapter:** 14 · LLMOps and SRE (`exercises/ch14-llmops-and-sre/`) · **Covers:** R26 On-site embedding, R29 Troubleshooting, R06 Cloud environments

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

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch14-llmops-and-sre/ex63-env-preflight`.
- **Expected output:** all 5 tests fail against the starter; when you're done, all 5 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch14-llmops-and-sre/ex63-env-preflight`: all 5
  pass.
- **Tests:** `test_preflight.py` (5 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Checks use injected resolvers and connectors, and each is one probe at one moment. In
  production, add checks for proxies, TLS interception and certificate chains, and have the customer run the script
  from the network segment the service will use.

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
Implement exercises/ch14-llmops-and-sre/ex63-env-preflight/starter.py so that test_preflight.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Check`,
`Report`, `python_version`, `env_vars`, `disk_free`, `dns`, `tcp`, `clock_skew`, `writable`, `run_preflight`.
Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the
README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch14-llmops-and-sre/ex63-env-preflight` and show me the output. If the README and the tests disagree, stop
and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Customer-environment preflight checker" as a senior forward deployed engineer would before it
ships to a customer. Specifically: Can one check that raises stop the others? Are hints shown only on failure? Would
a customer's IT team understand the output without you on the call? Rank findings by customer impact, quote the line
for each, and say which ones a test should catch.
```
