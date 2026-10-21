# ex25 hints · Schema drift detection

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

`infer_type` is a chain of `isinstance` checks, and the order matters. In Python `True` is an instance of `int`, so
test for `bool` before `int`. Strings are `str` unless `datetime.fromisoformat` accepts them.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **infer_schema:** collect column names across all records, keeping first-seen order. For each column, gather the
  set of inferred types (a missing key counts as `None`). Merge the set: remove `null`; one type left is that type;
  `{int, float}` becomes `float`; any other mix becomes `str`.
- **diff:** loop over the sorted union of column names and classify each one. A column can produce two changes, a
  type change *and* a nullability change.
- **migration_sql:** one line per change, in the same order.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Be strict about what counts as a datetime. A bare number string such as `"12"` must stay `str`. Requiring a `-` in
  the value is a simple guard that doesn't depend on the Python version's `fromisoformat` rules.
- Only `int -> float` is a widening (warn). `float -> int` is an error.
- Report nullability only one way: not-null becoming nullable. Nullable becoming not-null is fine.
- `migration_sql` returns a **list** of strings (the test checks `len(sql) == 5`).
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_infer_type` | `bool` checked after `int`; `"12"` classified as a datetime |
| `test_infer_schema` | Missing keys not treated as nullable; `bool` mixed with `str` not collapsed to `str` |
| `test_diff` | Not sorted by column; widening severity wrong; detail format isn't `int->float` |
| `test_migration_sql` | Returning one joined string; wrong SQL type map; comment format differs |
| `test_narrowing_and_empty` | `float->int` treated as a widening; empty input raises |
