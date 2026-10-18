import { test } from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { pathToFileURL } from "node:url";

const dir = process.env.CAP_DIR;
if (!dir) throw new Error("CAP_DIR not set (run via pytest)");
const m = await import(pathToFileURL(path.join(dir, "web", "answer_view.ts")).href);

const base = { intent: "policy_question", citations: ["homeowners"], abstained: false, escalated: false };

test("citations become footnote links and sources are listed", () => {
  const html = m.renderAnswer({ ...base, text: "Burst pipes are covered [1].", chunk_ids: ["homeowners#water-damage"] });
  assert.match(html, /covered <sup><a href="#src-1">1<\/a><\/sup>\./);
  assert.match(html, /<li id="src-1">homeowners#water-damage<\/li>/);
});

test("model and customer text is escaped", () => {
  const html = m.renderAnswer({ ...base, text: '<img src=x onerror="alert(1)"> [1]', chunk_ids: ["a<b"] });
  assert.ok(!html.includes("<img"));
  assert.ok(html.includes("&lt;img") && html.includes("a&lt;b"));
});

test("abstained and escalated states", () => {
  assert.match(m.renderAnswer({ ...base, text: "Not found", chunk_ids: [], abstained: true }), /class="answer abstained"/);
  assert.match(m.renderAnswer({ ...base, text: "Agent", chunk_ids: [], escalated: true }), /class="answer escalated"/);
});
