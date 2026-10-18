# ex59 · CI pipeline as code

**Module:** m11 · **Covers:** R07 CI/CD · **Time:** 45 min

## Learning objectives
- Write CI workflows that pass a security audit.
- Apply least-privilege tokens, pinned actions, timeouts and deploy gates.
- Lint workflows as code.

## Scenario
The customer's security team audits every GitHub Actions workflow that touches their repos: least-privilege token
permissions, pinned actions, timeouts, no secrets echoed to logs, deploys only from `main` and only after tests pass.

## Your task
1. `lint_workflow(doc: dict) -> list[str]` (parsed YAML; note PyYAML parses the key `on` as `True` — handle both):
   | rule | fails when |
   |---|---|
   | `triggers` | the workflow doesn't run on both `pull_request` and `push` |
   | `permissions` | no top-level `permissions`, or it is `write-all`, or grants any `write` scope other than `id-token` |
   | `timeout:<job>` | a job has no `timeout-minutes` |
   | `pin:<job>` | a step `uses:` an action at a branch ref (`@main`, `@master`) or with no ref |
   | `secret-echo:<job>` | a `run:` contains `echo` and `${{ secrets.` on the same line |
   | `matrix` | no job uses `strategy.matrix` with ≥ 2 python versions under key `python-version` |
   | `deploy-gate` | a job named `deploy` lacks `needs` including `test`, or lacks an `if` mentioning `refs/heads/main` |
2. Write `ci.yml` in this directory (jobs `test` and `deploy`) that has **no** issues; the test job must run `pytest`.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "CI pipeline as code". Before I write
code, teach me GitHub Actions security: permissions, action pinning, secret handling, matrix builds and gated
deploys. Use short Python examples that are not the exercise solution. Then ask me three questions to check my
understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m11-deploy-operate/ex59-ci-pipeline/starter.py so that test_ci.py passes. README.md in that
folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `lint_workflow`.
Also create ci.yml in the same folder, exactly as the README specifies. Constraints: Python 3.11+, the standard
library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests
or fde_kit. When you're done, run `pytest exercises/m11-deploy-operate/ex59-ci-pipeline` and show me the output. If
the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "CI pipeline as code" as a senior forward deployed engineer would before it ships to a
customer. Specifically: Is the 'on' key handled when YAML parses it as True? Would pinning to a tag satisfy a strict
auditor, or only a commit SHA? Can a pull request from a fork reach the deploy job? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
