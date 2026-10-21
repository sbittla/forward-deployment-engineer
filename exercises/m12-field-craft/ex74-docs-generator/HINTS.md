# ex74 hints · API reference and quickstart generator

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

For `public_api`, the key test is `obj.__module__ == module.__name__`. That's how you tell a function defined in the
module from one it imported (`from os import path`). Combine it with `inspect.isfunction` or `inspect.isclass`, skip
names starting with `_`, and use `__all__` instead whenever the module defines it.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **Docstrings:** run `inspect.cleandoc` first to remove the common indentation. The summary is the first paragraph,
  joined onto one line. Then walk the lines, switching sections on `Args:` and `Returns:`.
- **Args:** a line that matches `name (type): desc` or `name: desc` at the shallow indent starts an argument. Deeper
  lines are continuations, appended with a space.
- **Signatures:** `str(inspect.signature(fn))` gives `(query: str, limit: int = 10) -> list`. For classes, take
  `__init__`'s signature, drop `self`, and drop the return annotation.
- **missing_docs:** public items without `__doc__`, plus public functions in each public class's `vars(cls)` without
  one.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Tell continuation lines from new arguments by indentation, not by whether the line contains a colon (a description
  can contain one).
- `parse_google_docstring(None)` and `("")` return the empty structure, not an error.
- `missing_docs` is sorted, so `ClaimsClient.update` comes before `get_claim` (uppercase sorts before lowercase).
- Private methods (`_sign`) and dunder methods (`__init__`) are never reported.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_public_api` | Imported names included; `__all__` ignored |
| `test_parse_docstring` | Continuation line treated as a new argument; type in parentheses left in the name |
| `test_render` | Class signature still contains `self` or `-> None`; module docstring's later paragraphs included |
| `test_missing_docs` | `__init__` or private methods reported; result not sorted |
| `test_empty_module` | Empty docstring or empty module raises |
