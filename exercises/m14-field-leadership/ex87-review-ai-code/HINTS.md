# ex87 hints · Review and fix an AI-agent-written pull request; write agent instructions

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Review before you fix. Read each function in `starter.py` and write the `REVIEW.md` bullet first: what's wrong, how
you'd exploit or trigger it, and the fix. Then make the fixes one test at a time. Six functions, six findings; three
of them are security problems.
</details>

<details>
<summary>Hint 2 · The approach</summary>

The six defect classes, one per function:

- string-built SQL;
- a user-supplied path that isn't contained in `out_dir`;
- CSV joined by hand;
- an off-by-one page range;
- a credential written to a log;
- a bare `except` returning an empty result.

Plus a mutable default argument (`tag_counts`). The standard library fixes almost all of them: query parameters,
`os.path.realpath` plus a containment check, `csv.writer`, `range(1, n + 1)`, and letting exceptions propagate with
context.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Path checks must reject `../escape.csv`, `/etc/passwd` **and** `..\escape.csv`. On Linux a backslash is a legal
  filename character, so reject path separators in the filename outright, as well as checking where the resolved path
  ends up.
- Open the CSV with `newline=""`, or you get blank lines between rows on Windows.
- `load_tickets` should let `FileNotFoundError` through untouched, and wrap `JSONDecodeError` in a `ValueError` that
  names the file.
- The `REVIEW.md` format is checked by regex: `- [category] file:function: problem → fix`, using the `→` character.
  It must mention "SQL injection", "path traversal" and the token.
- `AGENT_INSTRUCTIONS.md` needs the five named sections, the test command in backticks, and a "Never do" section that
  covers secrets, SQL and paths.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_sql_injection` | Query still built with an f-string |
| `test_export_safe_and_quoted` | Backslash filename accepted; fields not quoted; extra blank lines in the CSV |
| `test_pagination` | Range stops before the last page |
| `test_token_not_logged` | Token still interpolated into a log line |
| `test_load_errors` | Errors swallowed; `ValueError` doesn't name the file |
| `test_no_shared_state` | Default dict still shared between calls |
| `test_review_md` | Bullet format doesn't match (missing `→` or `file:function:`); too few findings or security findings |
| `test_agent_instructions` | A section missing; no backticked `pytest` command; "Never do" lacks secrets, SQL or path |
