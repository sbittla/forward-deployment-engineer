# ex30 · Demo chat UI served from Python

**Module:** m05 · **Covers:** R02 Full-stack web, R21 Rapid prototyping & demos · **Time:** 60 min

## Learning objectives
- Ship a demo web app that cannot fail on the customer's Wi-Fi.
- Render model output safely with textContent, never innerHTML.
- Make demo mode visible and the real model one switch away.

## Scenario
Tomorrow at 9 a.m. you demo to the customer's VP. No time for a React build pipeline, and the demo laptop is the
customer's locked-down Windows machine. You need a single-file web app: Python standard-library server, vanilla
HTML/JS frontend, a fake model by default so the demo **cannot** fail on Wi-Fi, and a visible banner saying so.

## Your task
`make_app(llm, demo_mode: bool) -> ThreadingHTTPServer` (bind `127.0.0.1`, port 0):

- `GET /` → `text/html; charset=utf-8` page containing:
  - `<form id="chat-form">` with an `<input name="q">` and a submit button
  - `<div id="log">` where messages are appended
  - inline `<script>` that `fetch("/api/chat", {method: "POST", ...})` and renders the answer using
    `textContent` (never `innerHTML` — the customer will paste real data)
  - when `demo_mode` is True, an element with `id="demo-banner"` containing `DEMO MODE`
- `POST /api/chat` with JSON `{"q": str, "history": [{"role","content"}...]}` → calls
  `llm.complete(history + [{"role": "user", "content": q}], system=SYSTEM_PROMPT)` and returns
  `{"answer": text, "model": response.model, "latency_ms": int}`. Invalid input → 400 JSON error.
- Anything else → 404.

`SYSTEM_PROMPT` (module constant) must tell the model it is a support copilot that answers concisely and says
when it does not know.

## Field notes
Demo with the fake model, then flip one env var to show the real one if the network allows. Rehearse the failure
path: what do you say if the real model is slow?

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Demo chat UI served from Python".
Before I write code, teach me building a minimal demo stack with the Python standard library and vanilla JS,
XSS-safe rendering, and how to rehearse failure paths for a live demo. Use short Python examples that are not the
exercise solution. Then ask me three questions to check my understanding, one at a time, and tell me what to re-read
if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m05-fullstack-typescript/ex30-demo-web-ui/starter.py so that test_demo_ui.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `make_app`.
Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is allowed where the
README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/m05-fullstack-typescript/ex30-demo-web-ui` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Demo chat UI served from Python" as a senior forward deployed engineer would before it ships
to a customer. Specifically: Is there any path where model or user text reaches innerHTML? Does invalid JSON return
a 400 instead of a crash? Would the demo banner be obvious on a projector? Rank findings by customer impact, quote
the line for each, and say which ones a test should catch.
```
**Production prompt (what this exercise's code sends to a model)**
```text
You are a support copilot for the customer's service desk agents. Answer the agent's question concisely, in at most four sentences, using plain language. If you don't know the answer or it depends on account details you can't see, say so and suggest what the agent should check.
```
