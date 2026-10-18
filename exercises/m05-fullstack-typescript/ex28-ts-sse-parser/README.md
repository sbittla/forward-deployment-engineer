# ex28 · TypeScript: SSE token-stream parser

**Module:** m05 · **Covers:** R02 TypeScript, R08 LLM application development · **Time:** 50 min

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
