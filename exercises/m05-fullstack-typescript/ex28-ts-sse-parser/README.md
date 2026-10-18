# ex28 · TypeScript: SSE token-stream parser

**Module:** m05 · **Covers:** R02 TypeScript, R08 LLM application development · **Time:** 50 min

## Learning objectives
- Parse Server-Sent Events correctly under arbitrary re-chunking.
- Decode UTF-8 streams without splitting multi-byte characters.
- Accumulate streamed LLM text deltas and surface stream errors.

## Scenario
LLM APIs stream tokens as Server-Sent Events. The customer's corporate proxy re-chunks the stream arbitrarily —
an event can be split mid-line, and a UTF-8 emoji can be split mid-byte. Naive `chunk.split("\n")` parsing
corrupts answers about 1 in 50 times. Write the parser properly.

## Your task (`starter.ts`)
1. `class Utf8Chunker` with `push(bytes: Uint8Array): string` and `end(): string` — decode bytes to text without
   breaking multi-byte characters across chunks (hint: `TextDecoder` with `{ stream: true }`).
2. `class SSEParser` with `push(text: string): SSEEvent[]` and `end(): SSEEvent[]`, where
   `SSEEvent = { event: string; data: string }`:
   - lines end with `\n` or `\r\n`; a blank line dispatches the current event
   - `event: name` sets the type (default `"message"`); `data: x` appends a data line (multiple data lines are joined
     with `\n`); one leading space after the colon is removed; lines starting with `:` are comments
   - an event with no data lines is not dispatched; `end()` flushes a final event if the stream lacks a trailing blank line
3. `accumulateText(events: SSEEvent[]): string` — for Anthropic-style streams: concatenate
   `JSON.parse(data).delta.text` for every `content_block_delta` event whose delta type is `text_delta`; stop at
   `message_stop`; throw `Error(<error.message>)` on an `error` event; ignore everything else (`ping`, etc.).

## Run
```
node --test exercises/m05-fullstack-typescript/ex28-ts-sse-parser/sse.test.ts
```

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
Implement exercises/m05-fullstack-typescript/ex28-ts-sse-parser/starter.ts so that sse.test.ts passes. README.md in
that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `Utf8Chunker`,
`SSEParser`, `accumulateText`. Constraints: TypeScript executed directly by Node 23.6+ type stripping: no npm
packages, no build step, and only erasable type syntax (no enums, namespaces or parameter properties). Do not modify
the tests. When you're done, run `node --test exercises/m05-fullstack-typescript/ex28-ts-sse-parser/sse.test.ts` and
show me the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "TypeScript: SSE token-stream parser" as a senior forward deployed engineer would before it
ships to a customer. Specifically: What happens to an event split exactly at '\r' and '\n'? Is a final event without
a trailing blank line flushed? Could an error event be ignored? Rank findings by customer impact, quote the line for
each, and say which ones a test should catch.
```
