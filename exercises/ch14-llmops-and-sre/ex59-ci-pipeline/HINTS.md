# ex59 hints · CI pipeline as code

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Read the triggers with `doc.get("on", doc.get(True))`. PyYAML follows YAML 1.1, which turns the bare key `on` into the
boolean `True`. Then normalize the triggers into a set of event names, whether the YAML gave you a string, a list or a
dict.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **permissions:**
  - missing, or `write-all`: fails;
  - another string: passes only if it's `read-all`;
  - a dict: fails if any scope is `write`, except `id-token`.
- **Per job:** check `timeout-minutes`; then for each step's `uses`, check the ref after `@` (a missing ref, `main` or
  `master` fails); then check each line of each `run` for `echo` and `${{ secrets.` together.
- **matrix:** a flag that becomes true if *any* job has at least two `python-version` entries.
- **deploy-gate:** only applies if there's a job called `deploy`. `needs` can be a string or a list.
- Then write `ci.yml` so that it passes your own linter, with a `pytest` step in `test`.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- A commit SHA after `@` is pinned, and so is a version tag like `@v4`. Only branch names and missing refs fail.
- Check the echo rule line by line: a secret passed through `env:` on the deploy step is fine, but
  `echo "token=${{ secrets.X }}"` is not.
- `contents: read` with `id-token: write` passes. OIDC needs `id-token: write`, and that's the one exception.
- Each issue appears once per job, however many steps break the same rule.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_good` | The `on` key read only as a string, so the triggers look missing; `id-token: write` flagged |
| `test_bad` | `permissions: write-all` (a string) not handled; one issue reported per step instead of per job |
| `test_write_scope_and_unpinned` | `uses` with no `@` treated as pinned; `if` condition not checked for `refs/heads/main` |
| `test_your_workflow` | Your `ci.yml` breaks a rule, lacks a `deploy` job, or the test job doesn't run `pytest` |
| `test_long_lived_cloud_key_flagged` | Only step `env` searched, not job-level `env`; secret names matched without the `secrets.` prefix |
