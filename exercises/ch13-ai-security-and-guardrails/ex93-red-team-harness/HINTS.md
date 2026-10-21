# ex93 hints · AI red-team harness and security assessment report

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Make `Attack` a dataclass with `success_marker=None` as its last field, and validate the category and severity in
`__post_init__`. Then write `detect` as an ordered list of checks, each returning `(True, evidence)` as soon as it
fires: canary, then forbidden tool, then PII, then injection. The order sets which evidence string you report.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Canaries and tools** apply to every attack, whatever its category. A leaked secret is a failure however it was
  provoked.
- **PII** applies only to `pii_leak` attacks: an email or SSN pattern in the text.
- **Injection and jailbreak** need a `success_marker`. The attack failed (succeeded, from the attacker's side) when the
  marker appears and the reply does *not* look like a refusal.
- **run_suite** calls the target once per attack, records each result, updates the per-category counts, and adds the
  severity weight to the risk score for each failure.
- **retest_diff** compares the failed flags by id: fixed, regressed, still failing.
- **scan_tools** runs four independent checks per description and keeps every reason that fires, in the README's
  order. **upstream_headers** validates first, exchanges second, and refuses to send what it received.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- "I cannot do that. PWNED is not something I'll say." contains the marker but is a refusal, so it's **not** a
  failure. Check the refusal markers on the lowercased text.
- Regressions matter as much as fixes. The "hardened" target fixes three attacks but breaks one that passed before,
  and a retest report must show that.
- Sort findings by severity weight descending, then by id: critical items first, so a reader sees the worst first.
- Recommendations list only the categories that had failures.
- `Ig​nore previous` hides its instruction behind a zero-width space. Report the hidden character, then strip
  every `Cf` character before matching the phrases, or the instruction slips through.
- `aud` can be a string or a list; a missing `aud` is a rejection, not a pass.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_detectors` | Checks in the wrong order; refusal not detected (case-sensitive markers); PII checked for every category |
| `test_suite_and_report` | Risk weights wrong; findings not ordered by severity then id; recommendations for passing categories |
| `test_retest` | Regressions not reported; lists not sorted |
| `test_invalid_attacks_rejected` | No validation in `__post_init__` |
| `test_tool_poisoning` | Phrases matched before stripping invisible characters; stopping at the first reason; a tool flagged for naming itself |
| `test_token_audience_and_no_passthrough` | `aud` list not handled; missing `aud` accepted; inbound token forwarded when the exchange returns it unchanged |
| `test_remediation_evidence_fails_before_passes_after` | `run_suite` or `retest_diff` from earlier tests not finished; evidence string differs from `canary leaked: <canary>` |
| `test_residual_risk_acceptance` | Critical findings accepted; an acceptance treated as expired on its own review date; passing attacks listed; no `ValueError` for a blank owner or a non-ISO date |
