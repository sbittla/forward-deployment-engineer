import { test } from "node:test";
import assert from "node:assert/strict";

const m = process.env.FDE_SOLUTIONS
  ? await import(new URL("../../../solutions/exercises/m05-fullstack-typescript/ex28-ts-sse-parser/solution.ts", import.meta.url).href)
  : await import("./starter.ts");

const delta = (t: string) =>
  `event: content_block_delta\ndata: ${JSON.stringify({ type: "content_block_delta", delta: { type: "text_delta", text: t } })}\n\n`;

const STREAM =
  "event: message_start\ndata: {\"type\":\"message_start\"}\n\n" +
  ": keep-alive comment\n" +
  "event: ping\ndata: {}\n\n" +
  delta("Hello, ") + delta("wörld 👋") +
  "event: message_stop\ndata: {\"type\":\"message_stop\"}\n\n" +
  delta("IGNORED");

test("whole stream", () => {
  const p = new m.SSEParser();
  const evs = [...p.push(STREAM), ...p.end()];
  assert.equal(evs[0].event, "message_start");
  assert.equal(m.accumulateText(evs), "Hello, wörld 👋");
});

test("arbitrary byte chunking incl. split emoji and CRLF", () => {
  const bytes = new TextEncoder().encode(STREAM.replaceAll("\n", "\r\n"));
  for (const size of [1, 2, 3, 5, 7, 64]) {
    const dec = new m.Utf8Chunker();
    const p = new m.SSEParser();
    const evs: any[] = [];
    for (let i = 0; i < bytes.length; i += size) evs.push(...p.push(dec.push(bytes.slice(i, i + size))));
    evs.push(...p.push(dec.end()), ...p.end());
    assert.equal(m.accumulateText(evs), "Hello, wörld 👋", `chunk size ${size}`);
  }
});

test("multi-line data, default event, leading space, no-data events", () => {
  const p = new m.SSEParser();
  const evs = p.push("data:line1\ndata: line2\n\nevent: empty\n\n");
  assert.deepEqual(evs, [{ event: "message", data: "line1\nline2" }]);
});

test("end flushes final event", () => {
  const p = new m.SSEParser();
  assert.deepEqual(p.push("event: x\ndata: 1"), []);
  assert.deepEqual(p.end(), [{ event: "x", data: "1" }]);
});

test("error event throws", () => {
  const p = new m.SSEParser();
  const evs = p.push(delta("partial") + 'event: error\ndata: {"type":"error","error":{"type":"overloaded_error","message":"Overloaded"}}\n\n');
  assert.throws(() => m.accumulateText(evs), { message: "Overloaded" });
});
