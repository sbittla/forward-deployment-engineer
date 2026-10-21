# ex28 hints · TypeScript: SSE token-stream parser

Open a hint only after you've been stuck for about ten minutes. Each one gives away more than the last.

<details>
<summary>Hint 1 · Where to start</summary>

`Utf8Chunker` is a few lines: keep one `TextDecoder` for the whole stream, call `decode(bytes, { stream: true })` in
`push`, and `decode()` with no arguments in `end` to flush. The decoder holds incomplete multi-byte sequences until the
rest arrives. Then focus on the parser.
</details>

<details>
<summary>Hint 2 · The approach</summary>

The parser keeps three pieces of state:

- a **text buffer** of what's arrived but isn't yet a complete line;
- the current event name (starting as `"message"`);
- the list of data lines.

`push` appends to the buffer, then repeatedly cuts off everything up to the next `\n` and handles that line. Whatever
is left after the last `\n` waits for the next chunk.

Handle each line like this:

- blank line: dispatch the event (if it has data lines) and reset the state;
- starts with `:`: a comment, skip it;
- otherwise: split at the first `:` into field and value.
</details>

<details>
<summary>Hint 3 · The tricky part</summary>

- Split only on `\n`, then strip a trailing `\r` from the line. If you split on `\r\n`, a chunk boundary between the
  `\r` and the `\n` breaks it.
- Remove only **one** leading space from the value, not all whitespace.
- `end()` handles whatever is left in the buffer as a final line, then acts as if a blank line arrived.
- In `accumulateText`, check for `message_stop` *before* anything else, so deltas after it are ignored. For `error`
  events, throw `new Error(JSON.parse(data).error.message)`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `whole stream` | Comment lines treated as fields, or deltas after `message_stop` still added |
| `arbitrary byte chunking incl. split emoji and CRLF` | A new `TextDecoder` per chunk, or no `{ stream: true }`; lines split on `\r\n` across a chunk boundary |
| `multi-line data, default event, leading space, no-data events` | Data lines not joined with `\n`; an event with no data dispatched |
| `end flushes final event` | `end()` ignores the leftover buffer |
| `error event throws` | Error events skipped instead of thrown, or the wrong message field used |
