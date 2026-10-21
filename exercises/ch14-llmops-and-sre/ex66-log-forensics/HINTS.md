# ex66 hints · Log forensics: root-cause an incident

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Make `parse` strict: a line counts only if it's valid JSON, has `service` and `level`, and its `ts` parses with
`datetime.fromisoformat`. Anything else (blank lines included) increments the malformed count. Then sort by `ts`.
Python's sort is stable, so ties keep their original order for free.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **first_errors:** walk the sorted records and record the first ERROR timestamp per service.
- **Downstream set:** a recursive walk over `deps` with a `seen` set gives every service a service calls, directly or
  not.
- **root_cause:** a service is a candidate if none of its downstream services had an error **before** its own first
  error. Among the candidates, pick the earliest first error.
- **error_rate_by_minute:** group by service and `ts[11:16]` (`HH:MM`), counting errors and totals.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- The obvious answer is often wrong. The gateway shows the 502 that users saw, but it's the last service to fail.
  Root cause means following the dependency graph downward.
- `authsvc` also has no erroring dependencies, but its first error comes later. Hence "earliest first error wins".
- ISO timestamps in the same format compare correctly as strings, so you don't need datetimes for the ordering.
- No errors anywhere: `root_cause` returns `None`, and the summary prints `none` for both the root cause and the
  blast radius.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_parse` | Bad lines raise instead of being counted; records not sorted by `ts` |
| `test_first_errors_and_root` | Root cause picked as the earliest error overall without checking dependencies (or the reverse) |
| `test_error_rate` | Minute key taken from the wrong slice; minutes with no errors missing instead of 0.0 |
| `test_timeline` | Records not in time order, or the line format differs |
| `test_summary` | Blast radius not ordered by first error |
| `test_no_errors_and_garbage` | Blank line not counted as malformed; `min()` of an empty candidate list raises |
