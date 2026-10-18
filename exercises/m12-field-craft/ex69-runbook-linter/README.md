# ex69 · Runbook and handoff doc linter

**Module:** m12 · **Covers:** R24 Technical writing & enablement · **Time:** 50 min

## Scenario
An FDE engagement ends; the customer's ops team owns the system. If the runbook says "TODO: rollback steps", the
first incident will page *you* at 3 a.m. six months later. Lint handoff docs like code.

## Your task
`lint_runbook(markdown) -> list[str]` — issues formatted `"L<line>: <rule>"` (1-based line) or `"<rule>"` for
document-level problems:
- `missing-section:<name>` — each of `Overview`, `Prerequisites`, `Deploy`, `Rollback`, `Monitoring`,
  `Escalation` must appear as a heading (any level, case-insensitive, heading text may contain more words)
- `L<n>: placeholder` — a line containing `TODO`, `TBD` or `FIXME` (case-sensitive)
- `L<n>: code-lang` — an opening code fence without a language (closing fences are fine)
- `L<n>: heading-skip` — a heading more than one level deeper than the previous heading (e.g. `#` then `###`)
- `rollback-command` — the Rollback section contains no fenced code block
- `escalation-contact` — the Escalation section contains no email address and no phone number
- `undocumented-variable:<NAME>` — a `<NAME>` placeholder (upper-case letters/underscores) used inside a code
  block but not mentioned anywhere outside code blocks

Document-level issues come after line issues; keep each group in a stable order (sections in the order listed above,
variables in order of first use).

Then write `RUNBOOK.md` for the answer service (ex20/ex57/ex58) that passes the linter.
