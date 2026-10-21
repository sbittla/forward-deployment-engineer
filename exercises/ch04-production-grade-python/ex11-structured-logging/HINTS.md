# ex11 hints · Structured logging with correlation IDs

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Create one module-level `contextvars.ContextVar("correlation_id", default=None)`. Then write `correlation` with
`@contextlib.contextmanager`: set the variable, yield the id, and restore it afterwards.
`current_correlation_id()` just reads the variable.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- `ContextVar.set()` returns a token. Pass it to `reset(token)` in a `finally` block, which restores the *outer*
  value, so nested blocks work without a stack.
- In the formatter, build a dict from the record: `record.created` (a Unix timestamp) for `ts`,
  `record.levelname`, `record.name` and `record.getMessage()` (which applies the `%s` arguments). Anything passed as
  `extra={"fields": {...}}` appears as `record.fields`.
- Redact with a recursive function that walks dicts *and* lists.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- For the timestamp, use `datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()`. Without `tz`, you
  get local time with no offset.
- Compare keys with `str(k).lower()`, so `API_KEY` and `Authorization` are caught.
- Exceptions: `record.exc_info` is a tuple. Its first item's `__name__` gives `exc_type`, and
  `self.formatException(record.exc_info)` gives the traceback text.
- `logging.getLogger(name)` returns the same object each time. Only add your handler if it isn't already there, and
  set `propagate = False` so the root logger doesn't print a second copy.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_json_line_and_correlation` | Using `record.msg` (unformatted) instead of `record.getMessage()`; fields not merged at the top level; naive timestamp |
| `test_generated_and_nested` | Outer id not restored after the inner block (no token reset), or id isn't `uuid4().hex` |
| `test_redaction_nested` | Redaction doesn't recurse into lists, or compares keys case-sensitively |
| `test_exception_and_no_duplicate_handlers` | A handler added on every `get_logger` call, so each record is written twice |
| `test_fault_each_injected_failure_logged_with_correlation_id` | Correlation id read when the logger is created instead of in `format`, or exception info dropped |
| `test_fault_concurrent_failures_keep_their_own_correlation_id` | Correlation id stored in a global or thread-local instead of a `ContextVar` |
| `test_fault_exception_inside_block_restores_outer_id` | The id is restored after `yield` without a `finally`, so an exception skips the reset |
