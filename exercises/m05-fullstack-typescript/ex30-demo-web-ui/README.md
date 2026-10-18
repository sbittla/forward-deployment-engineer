# ex30 · Demo chat UI served from Python

**Module:** m05 · **Covers:** R02 Full-stack web, R21 Rapid prototyping & demos · **Time:** 60 min

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
