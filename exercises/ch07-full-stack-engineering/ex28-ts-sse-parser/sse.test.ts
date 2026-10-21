import { test } from "node:test";
import assert from "node:assert/strict";

const m = process.env.FDE_SOLUTIONS
  ? await import(new URL("../../../solutions/exercises/ch07-full-stack-engineering/ex28-ts-sse-parser/solution.ts", import.meta.url).href)
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

// Part B · a streaming client: authentication, cancellation, reconnection

test("parser tracks the last event id", () => {
  const p = new m.SSEParser();
  p.push("id: 7\nevent: delta\ndata: {}\n\n");
  assert.equal(p.lastEventId, "7");
  p.push("event: delta\ndata: {}\n\n");          // no id field: the last id carries over
  assert.equal(p.lastEventId, "7");
  p.push("id: bad\u0000id\ndata: {}\n\n");        // an id containing NUL is ignored
  assert.equal(p.lastEventId, "7");
  p.push("id: 9\n\n");                            // an id-only block still updates it
  assert.equal(p.lastEventId, "9");
});

const enc = (s: string) => new TextEncoder().encode(s);
const ev = (id: number, event: string, data: object) => `id: ${id}\nevent: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
const ANSWER = [ev(1, "delta", { text: "Flood " }), ev(2, "delta", { text: "is " }), ev(3, "delta", { text: "covered." }),
  ev(4, "done", {})];

// A fake BFF: replays events after Last-Event-ID; `dropAfter` closes the socket after that many events.
function fakeServer(opts: { status?: number; dropAfter?: number[]; events?: string[]; onChunk?: () => void } = {}) {
  const calls: any[] = [];
  const events = opts.events ?? ANSWER;
  const fetchFn = async (url: string, init: any) => {
    calls.push({ url, init });
    const status = opts.status ?? 200;
    const from = Number(init.headers["Last-Event-ID"] ?? 0);
    const drop = opts.dropAfter?.[calls.length - 1];
    async function* body() {
      let sent = 0;
      for (const e of events.slice(from)) {
        if (drop !== undefined && sent === drop) throw new TypeError("network error: socket hang up");
        yield enc(e);
        sent++;
        opts.onChunk?.();
      }
    }
    return { ok: status >= 200 && status < 300, status, body: body() };
  };
  return { fetchFn, calls };
}

test("stream: sends the bearer token and fails closed on 401 without retrying", async () => {
  const ok = fakeServer();
  const r = await m.streamAnswer(ok.fetchFn, "/api/chat/stream", { token: "t-123", body: { q: "flood?" } });
  assert.deepEqual(r, { status: "done", text: "Flood is covered.", lastEventId: "4", reconnects: 0 });
  assert.equal(ok.calls[0].init.method, "POST");
  assert.equal(ok.calls[0].init.headers.Authorization, "Bearer t-123");
  assert.equal(ok.calls[0].init.headers.Accept, "text/event-stream");
  assert.equal(ok.calls[0].init.body, JSON.stringify({ q: "flood?" }));
  assert.equal("Last-Event-ID" in ok.calls[0].init.headers, false);

  const expired = fakeServer({ status: 401 });
  await assert.rejects(m.streamAnswer(expired.fetchFn, "/s", { token: "old", maxReconnects: 5 }),
    (e: Error) => e instanceof m.AuthExpiredError && e.message === m.SESSION_EXPIRED);
  assert.equal(expired.calls.length, 1);          // never retried with a dead session

  const none = fakeServer();
  await assert.rejects(m.streamAnswer(none.fetchFn, "/s", { token: "" }), m.AuthExpiredError);
  assert.equal(none.calls.length, 0);             // no token: no request at all
});

test("stream: user cancellation stops reading and keeps the partial text", async () => {
  const ctrl = new AbortController();
  let chunks = 0;
  const srv = fakeServer({ onChunk: () => { if (++chunks === 1) ctrl.abort(); } });
  const r = await m.streamAnswer(srv.fetchFn, "/s", { token: "t", signal: ctrl.signal });
  assert.deepEqual(r, { status: "canceled", text: "Flood ", lastEventId: "1", reconnects: 0 });
  assert.equal(srv.calls[0].init.signal, ctrl.signal);   // the fetch can abort, so the BFF sees the disconnect
  assert.equal(srv.calls.length, 1);                      // a canceled stream never reconnects
});

test("stream: reconnects with Last-Event-ID and resumes without duplicates", async () => {
  const srv = fakeServer({ dropAfter: [2] });
  const r = await m.streamAnswer(srv.fetchFn, "/s", { token: "t" });
  assert.deepEqual(r, { status: "done", text: "Flood is covered.", lastEventId: "4", reconnects: 1 });
  assert.equal(srv.calls[1].init.headers["Last-Event-ID"], "2");
  assert.equal(srv.calls[1].init.headers.Authorization, "Bearer t");
});

test("stream: reconnects are bounded, and provider errors are not retried", async () => {
  const flaky = fakeServer({ dropAfter: [1, 0, 0, 0] });
  await assert.rejects(m.streamAnswer(flaky.fetchFn, "/s", { token: "t", maxReconnects: 2 }),
    { message: m.CONNECTION_LOST });
  assert.equal(flaky.calls.length, 3);            // the first attempt plus two reconnects

  const cut = fakeServer({ events: ANSWER.slice(0, 2) });   // ends cleanly but with no done event
  await assert.rejects(m.streamAnswer(cut.fetchFn, "/s", { token: "t", maxReconnects: 0 }),
    { message: m.CONNECTION_LOST });

  const failing = fakeServer({ events: [ev(1, "delta", { text: "Flo" }),
    ev(2, "error", { message: "The assistant is unavailable." })] });
  await assert.rejects(m.streamAnswer(failing.fetchFn, "/s", { token: "t" }),
    { message: "The assistant is unavailable." });
  assert.equal(failing.calls.length, 1);

  const down = fakeServer({ status: 503 });
  await assert.rejects(m.streamAnswer(down.fetchFn, "/s", { token: "t" }), { message: "The assistant is unavailable." });
  assert.equal(down.calls.length, 1);
});
