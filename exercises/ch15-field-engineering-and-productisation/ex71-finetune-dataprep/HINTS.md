# ex71 hints · Fine-tuning dataset preparation

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

Write `to_example` first. It's the heart of the pipeline. Map roles (customer becomes user, agent becomes assistant),
redact each turn's text, and merge into the previous message when the role repeats. Then drop messages from the end
until the last one is from the assistant, and prepend the system message.
</details>

<details>
<summary>Hint 2 · The approach</summary>

- **select:** resolved, CSAT not `None` and at least `min_csat`, and at least one agent turn.
- **Redaction order:** emails first, then phones, so digits inside an address aren't mistaken for a phone number.
- **dedupe:** build a key from the non-system message contents: lowercase, every digit replaced by `0`, whitespace
  collapsed. Keep the first example for each key.
- **split:** group by intent, then for each intent in sorted order shuffle with one seeded RNG and take the validation
  slice off the front.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- An intent with only one example puts 0 in validation (`"rare"` must stay in train). Otherwise it's
  `max(1, round(n * ratio))`.
- Replacing digits with `0` is what makes "order 101" and "order 202" duplicates. Templated conversations that differ
  only by ids teach the model nothing new.
- `to_example` raises `ValueError` when no assistant message is left after trimming.
- Token counts use `ceil(len(content) / 4)` for each message, summed. `stats` averages over train plus validation,
  rounded to 1 dp.
- Write JSONL as one `json.dumps` per line with a trailing newline.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `test_select` | `csat=None` compared with an int; conversations without agent turns kept |
| `test_to_example_merge_redact_trailing` | Same-role turns not merged with `\n`; trailing customer turn kept; phone redacted before email |
| `test_dedupe` | Digits not normalized, so near-duplicates survive |
| `test_split_stratified_no_overlap` | Single-example intent sent to validation; split not reproducible with the same seed |
| `test_token_filter_jsonl_stats` | Average computed over train only; JSONL written as one JSON array |
| `test_unusable_conversations` | No error raised when only customer turns exist |
