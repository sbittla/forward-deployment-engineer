# ex59 · CI pipeline as code

**Module:** m11 · **Covers:** R07 CI/CD · **Time:** 45 min

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
