# ex90 hints · Architecture decision records and partner design-review gate

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

`parse_adr` is three regexes: the title line (`^#\s+ADR-(\d+):\s*(.+)$` on the first line), the status line (a
multiline, case-insensitive search for `Status:` followed by one of the four values), and a multiline split on `## `
to get the sections. Lowercase each section's heading for the key, and strip its body.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **lint_adr:** report missing sections first, in the required order. Then run the content checks on the sections
  that exist: count the bullets under "alternatives considered", look for a downside word in "consequences", and look
  for `decided-by:` in "decision" when the status is accepted.
- **review_design:** one pass over `CHECKLIST` (area → severity), flagging missing or blank areas, plus the special
  PII rule. Sort by `(severity rank, area)`.
- **gate:** collect "reject" reasons and "conditional" reasons separately, in the README's order. Reject if there are
  any reject reasons (and list the conditional reasons after them), otherwise conditional if there are any, otherwise
  accept.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- A proposed ADR with only a Context section reports three `missing:` issues and nothing else. Don't run content
  checks on sections that don't exist.
- `decision:no-owner` applies only to **accepted** ADRs.
- The PII rule fires on "sent to model" *without* "redact". The healthy design mentions both, so it passes.
- Reason strings are exact: `tests 118/120`, `eval pass rate 0.85 < 0.9`, `major findings: 1`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_parse` | Status matched case-sensitively; a missing status doesn't raise; section keys not lowercased |
| `test_lint` | Content checks run on missing sections; issues out of order |
| `test_lint_rejects_negated_downside` | Downside words matched anywhere, so "no risk" counts; or the negation window crosses a clause boundary, so one denied word hides a real one |
| `test_review_design` | Blank strings not treated as missing; findings not sorted by severity then area |
| `test_gate` | Reasons in the wrong order or format; conditional reasons dropped when rejecting |
| `test_risk_acceptance` | Content checks run while fields are missing; `owner_org` compared case-sensitively; the 90-day limit applied to an expiry before the decision |
