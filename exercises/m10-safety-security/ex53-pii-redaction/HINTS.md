# ex53 hints · PII detection and redaction

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write `luhn_ok` first. It's a tiny, well-known algorithm: walking the digits from the right, double every second
digit, subtract 9 from any result above 9, sum everything, and check the total is divisible by 10. Then write one
regex per entity type and keep them in a list of `(type, pattern)` pairs.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- `detect` runs every pattern over the whole text and collects every match, then resolves overlaps in one pass. Sort
  by `(start, -length)` and keep a match only if it starts at or after the end of the last kept one.
- For credit cards, the regex only finds *candidates* (13–19 digits with optional single separators). Strip the
  separators and keep the match only if `luhn_ok` passes.
- `redact` walks the detected entities in order, copying the text between them and replacing each entity. In token
  mode, keep a dict from `(type, value)` to token, so a repeated value reuses its token.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- SSN rules fit neatly into negative lookaheads: `(?!000|666|9\d\d)` before the area, `(?!00)` before the group and
  `(?!0000)` before the serial.
- IPv4 octets need an alternation (`25[0-5]|2[0-4]\d|1?\d?\d`), because `\d{1,3}` accepts 300.
- Stop phone numbers matching inside longer digit runs: a lookbehind such as `(?<![\w-])` keeps a match from starting
  mid-number.
- Number tokens per type, in order of first appearance: the second distinct email is `[EMAIL_2]`, whatever came in
  between.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_detect_all` | Overlaps not resolved (a phone found inside the card number); results not sorted by start |
| `test_negatives` | SSN exclusions missing; card candidates not Luhn-checked; octets above 255 accepted |
| `test_phone_formats` | `+1` or `1-` prefix not optional; dot separators missing |
| `test_luhn` | Doubling the wrong digits (start from the right, second digit) |
| `test_offsets` | Offsets computed after changing the text, instead of from match positions |
| `test_mask` | Mask mode returns a non-empty mapping, or numbered tokens |
| `test_tokens_consistent_and_restore` | Same email gets two tokens; numbering shared across types |
