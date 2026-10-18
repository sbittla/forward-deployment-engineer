# ex69 · Runbook and handoff doc linter

**Module:** m12 · **Covers:** R24 Technical writing & enablement · **Time:** 50 min

## Learning objectives
- Lint runbooks and handoff docs like code.
- Require rollback commands, escalation contacts and documented variables.
- Write a runbook the customer's ops team can follow at 3 a.m.

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

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Runbook and handoff doc linter".
Before I write code, teach me what makes operational documentation usable (required sections, executable rollback
steps, contacts, no placeholders) and how to check it automatically. Use short Python examples that are not the
exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read
if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m12-field-craft/ex69-runbook-linter/starter.py so that test_runbook.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `lint_runbook`. Also
create RUNBOOK.md in the same folder, exactly as the README specifies. Constraints: Python 3.11+, the standard
library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests
or fde_kit. When you're done, run `pytest exercises/m12-field-craft/ex69-runbook-linter` and show me the output. If
the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Runbook and handoff doc linter" as a senior forward deployed engineer would before it ships
to a customer. Specifically: Are closing code fences ignored for the language rule? Are variables inside code blocks
matched only when documented outside? Could an on-call engineer roll back using only RUNBOOK.md? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
