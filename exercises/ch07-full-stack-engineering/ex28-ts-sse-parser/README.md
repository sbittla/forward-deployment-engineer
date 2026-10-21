# ex28 · TypeScript: SSE token-stream parser

**Chapter:** 7 · Full-Stack Engineering (`exercises/ch07-full-stack-engineering/`) · **Covers:** R02 TypeScript, R08 LLM application development

## Learning objectives
- Parse Server-Sent Events correctly under arbitrary re-chunking.
- Decode UTF-8 streams without splitting multi-byte characters.
- Accumulate streamed LLM text deltas and surface stream errors.
- Stream with an auth header, user cancellation and bounded reconnection that resumes from `Last-Event-ID`.

## Scenario
LLM APIs stream tokens as Server-Sent Events. The customer's corporate proxy re-chunks the stream arbitrarily —
an event can be split mid-line, and a UTF-8 emoji can be split mid-byte. Naive `chunk.split("\n")` parsing
corrupts answers about 1 in 50 times. Write the parser properly.

## Your task (`starter.ts`)
1. `class Utf8Chunker` with `push(bytes: Uint8Array): string` and `end(): string` — decode bytes to text without
   breaking multi-byte characters across chunks (hint: `TextDecoder` with `{ stream: true }`).
2. `class SSEParser` with `push(text: string): SSEEvent[]` and `end(): SSEEvent[]`, where
   `SSEEvent = { event: string; data: string }`:
   - lines end with `\n`, `\r\n` or a bare `\r` (a `\r\n` split across two chunks is one line ending); a blank
     line dispatches the current event
   - `event: name` sets the type (default `"message"`); `data: x` appends a data line (multiple data lines are joined
     with `\n`); one leading space after the colon is removed; lines starting with `:` are comments
   - an event with no data lines is not dispatched; `end()` returns `[]` and resets the parser: as the WHATWG spec
     says, an event the stream never terminated with a blank line is discarded, not dispatched
3. `accumulateText(events: SSEEvent[]): string` — for Anthropic-style streams: concatenate
   `JSON.parse(data).delta.text` for every `content_block_delta` event whose delta type is `text_delta`; stop at
   `message_stop`; throw `Error(<error.message>)` on an `error` event; ignore everything else (`ping`, etc.).
4. `SSEParser` also keeps `lastEventId: string` (initially `""`): an `id: x` line sets a buffer (ignored if the value
   contains a NUL character), and every blank line (dispatch) copies the buffer into `lastEventId`, even for a block
   with no data. The buffer carries over to later events that have no `id` line.

### Part B · A streaming client: authentication, cancellation, reconnection
`streamAnswer(fetchFn, url, opts) -> Promise<StreamResult>` reads the backend-for-frontend's stream (ex30's
events: `delta` with `{"text"}`, `done`, `error` with `{"message"}`). `opts` is
`{ token, body?, signal?, maxReconnects? }` (`maxReconnects` defaults to 2); the result is
`{ status: "done" | "canceled", text, lastEventId, reconnects }`. The starter gives you the types and the messages
`SESSION_EXPIRED`, `CONNECTION_LOST` and `UNAVAILABLE`, and an `AuthExpiredError` class to finish (its message is
`SESSION_EXPIRED`).

- **Authentication.** Each request is `fetchFn(url, { method: "POST", headers, body: JSON.stringify(opts.body ?? {}),
  signal })` with headers `Authorization: Bearer <token>`, `Accept: text/event-stream` and
  `Content-Type: application/json`. An empty token throws `AuthExpiredError` before any request (fail closed). A 401
  response throws `AuthExpiredError` and is never retried. Any other non-2xx status throws `Error(UNAVAILABLE)`.
- **Cancellation.** Pass `opts.signal` (from an `AbortController`) to `fetchFn`. If it's aborted, stop reading (check
  before handling each chunk, and when a read fails) and return `status: "canceled"` with the text so far. A canceled
  stream never reconnects.
- **Reconnection.** Decode chunks with `Utf8Chunker` and parse with `SSEParser`, tracking the parser's
  `lastEventId`. A `TypeError` from `fetchFn` or the body (how `fetch` reports network failures), or a body that ends
  without `done`, is a dropped connection: reconnect with the same headers plus `Last-Event-ID: <lastEventId>`, so
  the server resumes after that event and nothing is duplicated. After `maxReconnects` reconnects, throw
  `Error(CONNECTION_LOST)`.
- **Errors that aren't retried.** An `error` event throws `Error(<message>)`; malformed JSON throws as it is.

## Run
```
node --test exercises/ch07-full-stack-engineering/ex28-ts-sse-parser/sse.test.ts
```

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root;
  Node.js 22.18 or later (24 LTS recommended) for the TypeScript tests, with no `npm install`. No API key or network
  access is needed.
- **Run your work:** from the repository root,
  `node --test exercises/ch07-full-stack-engineering/ex28-ts-sse-parser/sse.test.ts`.
- **Expected output:** all 11 tests fail against the starter; when you're done, all 11 pass.
- **Check the reference solution:**
  `FDE_SOLUTIONS=1 node --test exercises/ch07-full-stack-engineering/ex28-ts-sse-parser/sse.test.ts` (PowerShell:
  `$env:FDE_SOLUTIONS=1; node --test exercises/ch07-full-stack-engineering/ex28-ts-sse-parser/sse.test.ts`): all 11
  pass.
- **Tests:** `sse.test.ts` (11 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root; a Node.js error about the `.ts` extension means Node is older than 22.18. For a failing test,
  [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The parser ignores the SSE `retry:` field, resuming works only if the server keeps each
  request's events and replays those after `Last-Event-ID` (ex30 does), and `accumulateText` works on a finished list
  of events. A production client also needs a timeout for a silent stream, an `AbortController` behind the Stop
  button, and a retry policy that doesn't send the user's question twice.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "TypeScript: SSE token-stream
parser". Before I write code, teach me the SSE wire format, streaming UTF-8 decoding, and the Anthropic streaming
event types (content_block_delta, message_stop, error). Use short TypeScript examples that are not the exercise
solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read if I get
one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch07-full-stack-engineering/ex28-ts-sse-parser/starter.ts so that sse.test.ts passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Utf8Chunker`,
`SSEParser`, `accumulateText`. Constraints: TypeScript executed directly by Node 22.18+ type stripping: no npm
packages, no build step, and only erasable type syntax (no enums, namespaces or parameter properties). Do not modify
the tests. When you're done, run `node --test exercises/ch07-full-stack-engineering/ex28-ts-sse-parser/sse.test.ts` and
show me the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "TypeScript: SSE token-stream parser" as a senior forward deployed engineer would before it
ships to a customer. Specifically: What happens to an event split exactly at '\r' and '\n'? Is a final event without
a trailing blank line flushed? Could an error event be ignored? Rank findings by customer impact, quote the line for
each, and say which ones a test should catch.
```
