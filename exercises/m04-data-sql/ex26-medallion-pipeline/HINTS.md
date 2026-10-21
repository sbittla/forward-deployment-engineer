# ex26 hints · Bronze / silver / gold mini lakehouse

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Bronze is a single list comprehension: keep every line, however broken. All the real work happens in silver. Start
there with one `_parse(row)` function that either returns a clean event dict or raises `ValueError` with a reason.
`silver` then catches the error and sends the row to quarantine.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **_parse** checks in order: JSON parses, required keys are present, `type` is valid, country normalises, amount is
  valid for purchases. Each failure has its own reason message.
- **Country:** lowercase and strip, look it up in `COUNTRY_ALIASES`; otherwise accept any two-letter alphabetic code
  upper-cased; otherwise reject it.
- **Dedupe:** keep a dict `event_id -> best event`, and replace the entry when `(ts, line_no)` is greater. Carry the
  line number on the event while you dedupe, then remove it before returning.
- **Gold:** one pass over the events, accumulating revenue, view counts and purchase counts.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- `round(10.555, 2)` in floating point gives `10.55`, but the expected value is `10.56`. Accumulate revenue as
  `Decimal(str(amount))` and use `quantize(Decimal("0.01"), ROUND_HALF_UP)`.
- `isinstance(True, int)` is True. Reject booleans as amounts explicitly, and reject strings such as `"abc"`.
- The day is the first 10 characters of `ts`; it stays an ISO string.
- A product with purchases but no views is left out of `conversion_by_product`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_bronze_keeps_everything` | Broken lines dropped at bronze, or `line_no` not 0-based |
| `test_silver` | Dedupe keeps the first occurrence instead of the latest `ts`; `usa` or `fr` not normalised; views missing `amount = 0.0` |
| `test_gold` | Float rounding gives `10.55`; country `uk` not mapped to `GB` |
| `test_quarantine_reasons` | Negative purchase amount or unknown type accepted; empty `gold([])` missing its keys |
