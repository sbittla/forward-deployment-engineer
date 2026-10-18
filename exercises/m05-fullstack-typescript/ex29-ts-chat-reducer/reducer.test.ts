import { test } from "node:test";
import assert from "node:assert/strict";

const m = process.env.FDE_SOLUTIONS
  ? await import(new URL("../../../solutions/exercises/m05-fullstack-typescript/ex29-ts-chat-reducer/solution.ts", import.meta.url).href)
  : await import("./starter.ts");

function run(actions: any[], start = m.initialState) {
  return actions.reduce((s: any, a: any) => m.reduce(s, a), start);
}

test("happy path streaming", () => {
  const s = run([
    { type: "send", id: "u1", text: "What is my deductible?" },
    { type: "stream_start", id: "a1" },
    { type: "delta", id: "a1", text: "Your deductible " },
    { type: "delta", id: "a1", text: "is $500." },
    { type: "stream_end", id: "a1" },
  ]);
  assert.equal(s.pending, false);
  assert.equal(s.messages.length, 2);
  assert.deepEqual(s.messages[1], { id: "a1", role: "assistant", text: "Your deductible is $500.", status: "done" });
  assert.equal(m.transcript(s), "user: What is my deductible?\nassistant: Your deductible is $500.");
});

test("no double send while pending, no empty send", () => {
  const s = run([{ type: "send", id: "u1", text: "hi" }, { type: "send", id: "u2", text: "again" }]);
  assert.equal(s.messages.length, 1);
  assert.equal(run([{ type: "send", id: "u1", text: "   " }]).messages.length, 0);
});

test("error then retry", () => {
  let s = run([
    { type: "send", id: "u1", text: "hi" },
    { type: "stream_start", id: "a1" },
    { type: "delta", id: "a1", text: "par" },
    { type: "stream_error", id: "a1", error: "overloaded" },
  ]);
  assert.equal(s.pending, false);
  assert.equal(s.error, "overloaded");
  assert.equal(m.transcript(s), "user: hi");
  s = m.reduce(s, { type: "retry" });
  assert.equal(s.messages.length, 1);
  assert.equal(s.pending, true);
  assert.equal(s.error, null);
  assert.equal(m.reduce(s, { type: "retry" }), s);
});

test("immutability and unknown ids", () => {
  const before = run([{ type: "send", id: "u1", text: "hi" }, { type: "stream_start", id: "a1" }]);
  const snapshot = JSON.stringify(before);
  const after = m.reduce(before, { type: "delta", id: "a1", text: "x" });
  assert.equal(JSON.stringify(before), snapshot);
  assert.notEqual(after.messages, before.messages);
  assert.deepEqual(m.reduce(after, { type: "delta", id: "zzz", text: "y" }).messages, after.messages);
  assert.deepEqual(m.reduce(after, { type: "clear" }), m.initialState);
});
