import { test } from "node:test";
import assert from "node:assert/strict";

const m = process.env.FDE_SOLUTIONS
  ? await import(new URL("../../../solutions/exercises/ch07-full-stack-engineering/ex91-react-copilot-ui/solution.ts", import.meta.url).href)
  : await import("./starter.ts");

// Minimal stand-ins with React's call signatures.
type El = { type: string; props: Record<string, any>; children: any[] };
const h = (type: string, props: Record<string, unknown> | null, ...children: unknown[]): El =>
  ({ type, props: props ?? {}, children: children.flat().filter((c) => c !== null && c !== undefined && c !== false) });

function makeUseReducer() {
  let state: any;
  const useReducer = (reducer: any, init: any) => {
    if (state === undefined) state = init;
    return [state, (a: any) => { state = reducer(state, a); }];
  };
  return { useReducer, get: () => state };
}

function find(el: any, pred: (e: El) => boolean): El[] {
  if (!el || typeof el !== "object") return [];
  return [...(pred(el) ? [el] : []), ...el.children.flatMap((c: any) => find(c, pred))];
}

test("reducer", () => {
  let s = m.chatReducer(m.initialState, { type: "draft", text: "  hi  " });
  const before = JSON.stringify(s);
  const s2 = m.chatReducer(s, { type: "send", id: "m1" });
  assert.equal(JSON.stringify(s), before);
  assert.deepEqual(s2.messages, [{ id: "m1", role: "user", text: "hi" }]);
  assert.equal(s2.pending, true);
  assert.equal(s2.draft, "");
  assert.equal(m.chatReducer(s2, { type: "send", id: "m2" }), s2);
  const s3 = m.chatReducer(s2, { type: "fail", error: "overloaded" });
  assert.equal(s3.error, "overloaded");
  assert.equal(s3.pending, false);
  const s4 = m.chatReducer(s3, { type: "retry" });
  assert.equal(s4.error, null);
  assert.equal(s4.pending, true);
});

test("hook sends, replies and retries", async () => {
  const rt = makeUseReducer();
  let calls: string[] = [];
  let fail = true;
  const api = async (t: string) => { calls.push(t); if (fail) throw new Error("timeout"); return "Answer: " + t; };
  const useChat = m.makeUseChat(rt.useReducer, api);
  let chat = useChat();
  chat.setDraft("Is flood covered?");
  chat = useChat();
  await chat.send();
  assert.equal(rt.get().error, "timeout");
  fail = false;
  chat = useChat();
  await chat.retry();
  const st = rt.get();
  assert.deepEqual(calls, ["Is flood covered?", "Is flood covered?"]);
  assert.deepEqual(st.messages.map((x: any) => [x.id, x.role, x.text]),
    [["m1", "user", "Is flood covered?"], ["m2", "assistant", "Answer: Is flood covered?"]]);
  assert.equal(st.pending, false);
});

test("panel renders accessible, safe markup", () => {
  const Panel = m.makeCopilotPanel(h);
  const events: string[] = [];
  const state = { messages: [{ id: "m1", role: "user", text: "<img onerror=x>" }, { id: "m2", role: "assistant", text: "Covered [1]" }],
    pending: true, error: "Model overloaded", draft: "next" };
  const el = Panel({ state, title: "Claims copilot", onDraft: (t: string) => events.push("draft:" + t),
    onSend: () => events.push("send"), onRetry: () => events.push("retry") }) as El;
  assert.equal(el.type, "section");
  assert.equal(el.props["aria-label"], "Claims copilot");
  const log = find(el, (e) => e.props.role === "log")[0];
  assert.equal(log.type, "ul");
  assert.equal(log.props["aria-live"], "polite");
  assert.deepEqual(log.children.map((li: El) => [li.props.key, li.props["data-role"], li.children[0]]),
    [["m1", "user", "<img onerror=x>"], ["m2", "assistant", "Covered [1]"]]);
  assert.equal(find(el, (e) => "dangerouslySetInnerHTML" in e.props).length, 0);
  const alert = find(el, (e) => e.props.role === "alert")[0];
  assert.ok(JSON.stringify(alert).includes("Model overloaded"));
  find(alert, (e) => e.type === "button")[0].props.onClick();
  const form = find(el, (e) => e.type === "form")[0];
  let prevented = false;
  form.props.onSubmit({ preventDefault: () => { prevented = true; } });
  const input = find(form, (e) => e.type === "input")[0];
  assert.equal(input.props.value, "next");
  assert.equal(input.props["aria-label"], "Message");
  input.props.onChange({ target: { value: "typed" } });
  const send = find(form, (e) => e.type === "button" && e.children.includes("Send"))[0];
  assert.equal(send.props.disabled, true);
  assert.equal(prevented, true);
  assert.deepEqual(events, ["retry", "send", "draft:typed"]);
  const calm = Panel({ state: { ...state, error: null, pending: false }, title: "t", onDraft() {}, onSend() {}, onRetry() {} });
  assert.equal(find(calm, (e) => e.props.role === "alert").length, 0);
});

test("hook: stop aborts the request and shows Stopped, not an error", async () => {
  const rt = makeUseReducer();
  let seen: AbortSignal | undefined;
  const api = (_t: string, signal?: AbortSignal) => new Promise<string>((_resolve, reject) => {
    seen = signal;
    signal?.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")));
  });
  const useChat = m.makeUseChat(rt.useReducer, api);
  let chat = useChat();
  chat.setDraft("Is flood covered?");
  chat = useChat();
  const sending = chat.send();
  chat = useChat();
  chat.stop();
  await sending;
  const st = rt.get();
  assert.equal(seen?.aborted, true);              // the fetch is aborted, so the BFF closes the upstream
  assert.equal(st.pending, false);
  assert.equal(st.stopped, true);
  assert.equal(st.error, null);                   // the user stopped it: no alert
  assert.deepEqual(st.messages.map((x: any) => x.role), ["user"]);
  chat = useChat();
  chat.stop();                                    // nothing in flight: no-op
  assert.equal(rt.get(), st);
});

test("hook: a 401 asks the user to sign in and never retries", async () => {
  const rt = makeUseReducer();
  const calls: string[] = [];
  const api = async (t: string) => {
    calls.push(t);
    throw Object.assign(new Error("Your session has expired. Sign in again."), { name: "AuthExpiredError" });
  };
  const useChat = m.makeUseChat(rt.useReducer, api);
  let chat = useChat();
  chat.setDraft("Is flood covered?");
  chat = useChat();
  await chat.send();
  assert.equal(rt.get().authExpired, true);
  assert.equal(rt.get().error, m.SESSION_EXPIRED);
  chat = useChat();
  await chat.retry();
  assert.deepEqual(calls, ["Is flood covered?"]);  // retry is a no-op until sign-in
  assert.equal(m.chatReducer(rt.get(), { type: "retry" }), rt.get());
});

test("panel: every failure state is announced with plain text and one labeled action", () => {
  const Panel = m.makeCopilotPanel(h);
  const base = { ...m.initialState, messages: [{ id: "m1", role: "user", text: "Is flood covered?" }] };
  const cases = [
    { name: "provider error", state: { ...base, error: "The assistant is unavailable." },
      role: "alert", text: "The assistant is unavailable.", action: "Retry" },
    { name: "connection lost", state: { ...base, error: "Connection lost. Check your network and retry." },
      role: "alert", text: "Connection lost. Check your network and retry.", action: "Retry" },
    { name: "session expired", state: { ...base, error: m.SESSION_EXPIRED, authExpired: true },
      role: "alert", text: m.SESSION_EXPIRED, action: "Sign in" },
    { name: "stopped", state: { ...base, stopped: true }, role: "status", text: m.STOPPED, action: null },
  ];
  for (const c of cases) {
    const clicks: string[] = [];
    const el = Panel({ state: c.state, title: "Claims copilot", onDraft() {}, onSend() {},
      onRetry: () => clicks.push("Retry"), onStop: () => clicks.push("Stop"), onSignIn: () => clicks.push("Sign in") });
    const regions = find(el, (e) => e.props.role === "alert" || e.props.role === "status");
    assert.equal(regions.length, 1, c.name);
    const [region] = regions;
    assert.equal(region.props.role, c.role, c.name);
    assert.equal(region.children[0], c.text, c.name);
    assert.doesNotMatch(c.text, /\b[45]\d\d\b|Error:|anthropic|openai/i, c.name);  // no codes, traces or providers
    const buttons = find(region, (e) => e.type === "button");
    assert.deepEqual(buttons.map((b) => b.children[0]), c.action ? [c.action] : [], c.name);
    for (const b of buttons) {
      assert.equal(b.props.type, "button", c.name);  // a real, keyboard-reachable button that doesn't submit
      b.props.onClick();
    }
    assert.deepEqual(clicks, c.action ? [c.action] : [], c.name);
  }
  const busy = Panel({ state: { ...base, pending: true }, title: "t", onDraft() {}, onSend() {}, onRetry() {},
    onStop() {} });
  assert.equal(find(busy, (e) => e.type === "button" && e.children.includes("Stop")).length, 1);
  const idle = Panel({ state: base, title: "t", onDraft() {}, onSend() {}, onRetry() {} });
  assert.equal(find(idle, (e) => e.type === "button" && e.children.includes("Stop")).length, 0);  // only in flight
});
