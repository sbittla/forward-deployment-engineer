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

- A line ends at the first `\r` or `\n`. After a `\r`, drop a `\n` if it's the next character, even when it
  arrives in the next chunk. Splitting on the string `\r\n` breaks when a chunk boundary falls between them.
- Remove only **one** leading space from the value, not all whitespace.
- `end()` dispatches nothing: an event without its closing blank line is discarded. Just reset the state.
- In `accumulateText`, check for `message_stop` *before* anything else, so deltas after it are ignored. For `error`
  events, throw `new Error(JSON.parse(data).error.message)`.
</details>

## When a test fails

| Test | Likely cause |
|---|---|
| `whole stream` | Comment lines treated as fields, or deltas after `message_stop` still added |
| `arbitrary byte chunking incl. split emoji and CRLF` | A new `TextDecoder` per chunk, or no `{ stream: true }`; lines split on `\r\n` across a chunk boundary; bare `\r` not a line end |
| `multi-line data, default event, leading space, no-data events` | Data lines not joined with `\n`; an event with no data dispatched |
| `bare CR ends a line, and a CRLF split across chunks is one line ending` | Only `\n` treated as a line end; the `\n` after a chunk-final `\r` read as a blank line |
| `end discards an unterminated event` | `end()` dispatches the partial event instead of discarding it |
| `error event throws` | Error events skipped instead of thrown, or the wrong message field used |
| `parser tracks the last event id` | `lastEventId` set when the `id` line is read instead of at dispatch; reset when an event has no `id`; NUL not rejected |
| `stream: sends the bearer token and fails closed on 401 without retrying` | Header name or `Bearer ` prefix wrong; 401 treated as a dropped connection and retried; empty token still sent |
| `stream: user cancellation stops reading and keeps the partial text` | `signal` not passed to `fetchFn`; abort not checked before each chunk; an abort counted as a dropped connection |
| `stream: reconnects with Last-Event-ID and resumes without duplicates` | `Last-Event-ID` missing on the retry, or the text reset on reconnect; a new parser not used per attempt |
| `stream: reconnects are bounded, and provider errors are not retried` | No reconnect limit; an `error` event or a 503 retried; a body ending without `done` returned as success |
