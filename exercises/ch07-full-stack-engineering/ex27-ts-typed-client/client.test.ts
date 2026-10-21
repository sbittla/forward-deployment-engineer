import { test } from "node:test";
import assert from "node:assert/strict";

const m = process.env.FDE_SOLUTIONS
  ? await import(new URL("../../../solutions/exercises/ch07-full-stack-engineering/ex27-ts-typed-client/solution.ts", import.meta.url).href)
  : await import("./starter.ts");

test("primitives", () => {
  assert.equal(m.str().parse("a"), "a");
  assert.equal(m.num().parse(3), 3);
  assert.equal(m.bool().parse(false), false);
  assert.throws(() => m.num().parse("3"), { message: "$: expected number" });
  assert.throws(() => m.num().parse(Number.NaN), { message: "$: expected number" });
});

test("nested paths", () => {
  const s = m.obj({ items: m.arr(m.obj({ id: m.num() })) });
  assert.throws(() => s.parse({ items: [{ id: 1 }, { id: 2 }, { id: "x" }] }), { message: "$.items[2].id: expected number" });
  assert.throws(() => s.parse([]), { message: "$: expected object" });
  assert.throws(() => s.parse({ items: "no" }), { message: "$.items: expected array" });
});

test("extra keys dropped, optional, literal", () => {
  const s = m.obj({ a: m.str(), b: m.optional(m.num()), p: m.literal("low", "high") });
  assert.deepEqual(s.parse({ a: "x", p: "low", extra: 1 }), { a: "x", b: undefined, p: "low" });
  assert.throws(() => s.parse({ a: "x", p: "mid" }), { message: "$.p: expected one of low|high" });
});

function fakeFetch(status: number, body: unknown, calls: unknown[] = []) {
  return async (url: string, init?: { headers?: Record<string, string> }) => {
    calls.push({ url, init });
    return { ok: status >= 200 && status < 300, status, json: async () => body };
  };
}

test("client validates and sends headers", async () => {
  const calls: any[] = [];
  const body = { id: 7, title: "Login broken", priority: "urgent", tags: ["auth"], internal: true };
  const c = m.createClient("https://api.example.com", fakeFetch(200, body, calls));
  const t = await c.getTicket(7);
  assert.equal(t.priority, "urgent");
  assert.equal((t as any).internal, undefined);
  assert.equal(calls[0].url, "https://api.example.com/tickets/7");
  assert.equal(calls[0].init.headers.Accept, "application/json");
});

test("client rejects drifted schema and http errors", async () => {
  const drifted = { id: 7, title: "x", priority: 3, tags: [] };
  await assert.rejects(m.createClient("https://a", fakeFetch(200, drifted)).getTicket(7),
    (e: Error) => e instanceof m.ValidationError && e.message.startsWith("$.priority"));
  await assert.rejects(m.createClient("https://a", fakeFetch(404, {})).getTicket(7),
    (e: any) => e instanceof m.HttpError && e.status === 404);
});
