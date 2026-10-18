# ex09 · Typed config and secrets loading

**Module:** m02 Production Python · **Covers:** R01 Python, R22 Production hardening, R17 Security · **Time:** 40 min

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
