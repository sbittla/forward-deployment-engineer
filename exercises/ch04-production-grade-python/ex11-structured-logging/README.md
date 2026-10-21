# ex11 · Structured logging with correlation IDs

**Chapter:** 4 · Production-Grade Python (`exercises/ch04-production-grade-python/`) · **Covers:** R01 Python, R15 Observability

## Learning objectives
- Emit one JSON log line per event with a correlation id across a request.
- Redact sensitive keys at any nesting depth before they reach the log sink.
- Use contextvars so correlation ids work with threads and asyncio.

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

### Fault-injection tests
The `test_fault_*` tests inject failures and check the logs explain them: a fake dependency fails requests 2, 5 and
7 of ten, and each `ERROR` line must carry that request's correlation id and `exc_type`; 20 interleaved `asyncio`
requests, every third one failing, must never log under another request's id; and an exception raised inside a
nested `correlation` block must still restore the outer id.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root,
  `pytest exercises/ch04-production-grade-python/ex11-structured-logging`.
- **Expected output:** all 7 tests fail against the starter; when you're done, all 7 pass.
- **Check the reference solution:**
  `pytest --solutions exercises/ch04-production-grade-python/ex11-structured-logging`: all 7 pass.
- **Tests:** `test_logging.py` (7 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** Redaction matches a fixed set of key names, so a secret or personal data inside a message
  string or under another key is logged as-is. Production adds value-pattern scanning or allow-listed fields, a
  correlation id propagated across service calls (an `X-Request-ID` or trace header), and retention and access
  controls on the log platform.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Structured logging with correlation
IDs". Before I write code, teach me structured logging, correlation ids, contextvars, and log redaction for
sensitive fields. Use short Python examples that are not the exercise solution. Then ask me three questions to check
my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch04-production-grade-python/ex11-structured-logging/starter.py so that test_logging.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`correlation`, `current_correlation_id`, `JsonFormatter`, `get_logger`. Constraints: Python 3.11+, the standard
library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not modify the tests
or fde_kit. When you're done, run `pytest exercises/ch04-production-grade-python/ex11-structured-logging` and show me the
output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Structured logging with correlation IDs" as a senior forward deployed engineer would before
it ships to a customer. Specifically: Do nested correlation blocks restore the outer id even when an exception is
raised? Is redaction case-insensitive and recursive into lists? Can calling get_logger twice duplicate lines? Rank
findings by customer impact, quote the line for each, and say which ones a test should catch.
```
