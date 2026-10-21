# Review: agent PR "ticket export utilities"

Verdict: request changes. Six defects, two of them exploitable. Tests now cover each one.

- [security] starter.py:find_tickets: SQL injection via an f-string query; `x' OR '1'='1` returns every customer's tickets → parameterized query with `?`
- [security] starter.py:export_csv: path traversal; `../` or an absolute filename writes anywhere on disk → resolve the path and refuse anything outside `out_dir`
- [security] starter.py:call_api: the API token is written to the log in plain text → log the action, never the credential
- [correctness] starter.py:export_csv: hand-joined CSV breaks on commas and quotes inside subjects → use `csv.writer`
- [correctness] starter.py:fetch_all: off-by-one drops the last page (`range(1, total_pages)`) → iterate to `total_pages + 1`
- [reliability] starter.py:load_tickets: bare `except Exception` returns `[]` on a missing or corrupt file, hiding data loss → let `FileNotFoundError` propagate and raise `ValueError` naming the file
- [correctness] starter.py:tag_counts: mutable default `counts={}` leaks counts between calls → default to `None` and build a fresh counter

Process note: the PR description said "all tests pass", but there were no tests. Ask the agent for failing tests first.
