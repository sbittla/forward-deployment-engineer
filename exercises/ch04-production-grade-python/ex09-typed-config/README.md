# ex09 · Typed config and secrets loading

**Chapter:** 4 · Production-Grade Python (`exercises/ch04-production-grade-python/`) · **Covers:** R01 Python, R22 Production hardening, R17 Security

## Learning objectives
- Validate all configuration at start-up and report every problem at once.
- Keep secrets out of logs, reprs and error messages by construction.
- Design typed settings that fail fast in the customer's environment.

## Scenario
Your demo worked on your laptop. In the customer's Kubernetes cluster it crashed on start-up with
`KeyError: 'API_KEY'`, then — after they fixed that — printed the API key into Splunk. Production services
validate **all** configuration up front, report every problem at once, and never log secrets.

## Your task
`load_settings(env: Mapping[str, str]) -> Settings` reading variables with the `FDE_` prefix:

| Var | Type | Rule | Default |
|---|---|---|---|
| `FDE_API_BASE_URL` | str | required, must start with `https://` | — |
| `FDE_API_KEY` | `Secret` | required, non-empty | — |
| `FDE_TIMEOUT_S` | float | > 0 | `30.0` |
| `FDE_MAX_RETRIES` | int | 0–10 | `3` |
| `FDE_LOG_LEVEL` | str | one of DEBUG/INFO/WARNING/ERROR (case-insensitive, stored upper) | `INFO` |
| `FDE_ALLOWED_TENANTS` | tuple[str] | comma-separated, whitespace stripped, empties dropped | `()` |

- Collect **all** problems and raise `ConfigError` whose `.errors` is a list of messages each naming the variable.
- `Secret`: `str()`/`repr()` return `"Secret('****')"`; `.reveal()` returns the value; equality compares values.
- `Settings.redacted() -> dict` — all fields, with the key shown as `"****"`.

## Field notes
Fail fast at start-up, not at 2 a.m. on the first request that touches the missing setting.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Typed config and secrets loading".
Before I write code, teach me twelve-factor configuration, fail-fast validation, and secret-handling patterns that
prevent API keys from reaching logs. Use short Python examples that are not the exercise solution. Then ask me three
questions to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch04-production-grade-python/ex09-typed-config/starter.py so that test_config.py passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `ConfigError`,
`Secret`, `Settings`, `load_settings`. Constraints: Python 3.11+, the standard library and the repo's fde_kit
package only (pyyaml is allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done,
run `pytest exercises/ch04-production-grade-python/ex09-typed-config` and show me the output. If the README and the tests
disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Typed config and secrets loading" as a senior forward deployed engineer would before it ships
to a customer. Specifically: Is there any code path (repr, exception text, f-string) that exposes the secret? Are
all errors collected before raising? How would you extend this to load secrets from a vault without changing
callers? Rank findings by customer impact, quote the line for each, and say which ones a test should catch.
```
