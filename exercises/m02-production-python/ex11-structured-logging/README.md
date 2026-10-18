# ex11 · Structured logging with correlation IDs

**Module:** m02 · **Covers:** R01 Python, R15 Observability · **Time:** 40 min

## Scenario
A customer reports "the copilot gave a wrong answer around 3 pm". Your logs are free-text `print`s from four
services. You cannot reconstruct one request end-to-end. Fix that for the next incident.

## Your task
1. `correlation(cid=None)` — a context manager that sets a `contextvars.ContextVar` for the duration of the
   block (generates `uuid4().hex` when `cid` is None) and yields the id. Nested blocks restore the outer id.
2. `current_correlation_id()` → the active id or `None`.
3. `JsonFormatter(logging.Formatter)` — `format(record)` returns one JSON object per line with keys
   `ts` (ISO-8601 UTC), `level`, `logger`, `msg` (the formatted message), `correlation_id`, plus every key passed via
   `extra={"fields": {...}}`. Keys in `SENSITIVE` (case-insensitive) at any nesting depth are replaced with
   `"[REDACTED]"`. If the record has exception info, add `exc_type` and `exc` (the formatted traceback).
4. `get_logger(name, stream)` — returns a logger writing JSON to `stream` at INFO, without duplicate handlers if
   called twice.
