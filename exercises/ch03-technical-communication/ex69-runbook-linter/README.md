# ex69 · Runbook and handoff doc linter

**Chapter:** 3 · Technical Communication (`exercises/ch03-technical-communication/`) · **Covers:** R24 Technical writing & enablement

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

The runbook is one page of the handover. [`examples/`](examples/) holds two more, filled in for the Northwind
reference engagement (Section 3.6, Table 3.6; fictional, illustrative numbers): a handover document built on the
playbook's operational readiness review, and an architecture decision record that passes ex90's `lint_adr`. They're
reading material; no test depends on them.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch03-technical-communication/ex69-runbook-linter`.
- **Expected output:** all 5 tests fail against the starter; when you're done, all 5 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch03-technical-communication/ex69-runbook-linter`:
  all 5 pass.
- **Tests:** `test_runbook.py` (5 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The linter checks structure, not correctness: a runbook with a wrong command or a stale
  contact still passes. Before handover, someone other than the author runs the rollback from the runbook alone, and
  the escalation contacts are checked against the customer's on-call rota.

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
Implement exercises/ch03-technical-communication/ex69-runbook-linter/starter.py so that test_runbook.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `lint_runbook`. Also
create RUNBOOK.md in the same folder, exactly as the README specifies. Constraints: Python 3.11+, the standard
library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests
or fde_kit. When you're done, run `pytest exercises/ch03-technical-communication/ex69-runbook-linter` and show me the output. If
the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Runbook and handoff doc linter" as a senior forward deployed engineer would before it ships
to a customer. Specifically: Are closing code fences ignored for the language rule? Are variables inside code blocks
matched only when documented outside? Could an on-call engineer roll back using only RUNBOOK.md? Rank findings by
customer impact, quote the line for each, and say which ones a test should catch.
```
