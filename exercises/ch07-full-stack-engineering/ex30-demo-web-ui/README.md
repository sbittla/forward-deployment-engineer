# ex30 · Demo chat UI served from Python

**Chapter:** 7 · Full-Stack Engineering (`exercises/ch07-full-stack-engineering/`) · **Covers:** R02 Full-stack web, R21 Rapid prototyping & demos

## Learning objectives
- Ship a demo web app that cannot fail on the customer's Wi-Fi.
- Render model output safely with textContent, never innerHTML.
- Make demo mode visible and the real model one switch away.
- Relay a streamed answer as server-sent events, and stop the upstream when the browser leaves.

## Scenario
Tomorrow at 9 a.m. you demo to the customer's VP. No time for a React build pipeline, and the demo laptop is the
customer's locked-down Windows machine. You need a single-file web app: Python standard-library server, vanilla
HTML/JS frontend, a fake model by default so the demo **cannot** fail on Wi-Fi, and a visible banner saying so.

## Your task
`make_app(llm, demo_mode: bool, api_token: str | None = None) -> ThreadingHTTPServer` (bind `127.0.0.1`, port 0):

- `GET /` → `text/html; charset=utf-8` page containing:
  - `<form id="chat-form">` with an `<input name="q">` and a submit button
  - `<div id="log">` where messages are appended
  - inline `<script>` that `fetch("/api/chat", {method: "POST", ...})` and renders the answer using
    `textContent` (never `innerHTML` — the customer will paste real data)
  - when `demo_mode` is True, an element with `id="demo-banner"` containing `DEMO MODE`
- `POST /api/chat` with JSON `{"q": str, "history": [{"role","content"}...]}` → calls
  `llm.complete(history + [{"role": "user", "content": q}], system=SYSTEM_PROMPT)` and returns
  `{"answer": text, "model": response.model, "latency_ms": int}`. Invalid input → 400 JSON error.
- `POST /api/chat/stream` with the same body and the same 400 validation → `200` with headers
  `Content-Type: text/event-stream`, `Cache-Control: no-cache` and `X-Accel-Buffering: no`, no `Content-Length`,
  and a body written by `relay`: one `delta` event per piece of the answer (at least two pieces for a multi-word
  answer, e.g. split after each word's trailing whitespace; the pieces concatenate to exactly `response.text`),
  then a `done` event, numbered with SSE ids from 1. The connection closes after the stream.
- **Resume.** The body may carry `"request_id"` (a string of 1 to 128 characters; anything else is a 400). With one,
  the server keeps the answer's pieces under the key (the request's `Authorization` header, `request_id`), at most
  `MAX_REPLAYS` (module constant, 256) answers, dropping the oldest. A `Last-Event-ID: n` header (digits only, else
  400) resumes: the server replays the kept pieces after the `n`th, with ids from `n + 1`, then `done`, without
  calling the model. If it holds nothing under that key (no `request_id`, another caller, an evicted answer), it
  answers `409 {"error": "cannot resume this stream"}` instead of generating a different answer. A repeat request
  with a kept `request_id` and no `Last-Event-ID` replays the whole answer.
- Anything else → 404.
- Both POST paths treat the request as untrusted, in this order, before any model call:
  1. **Size.** If `Content-Length` isn't an integer from 0 to `MAX_BODY_BYTES` (module constant, `64 * 1024`), answer
     `413 {"error": "body too large"}` without reading the body, and close the connection.
  2. **Authentication on the stream.** When `api_token` is set, the `Authorization` header must equal
     `Bearer <api_token>` (compare with `hmac.compare_digest`); otherwise answer `401 {"error": "unauthorized"}`.
     With `api_token=None` (the local demo) no header is needed.
  3. Then the JSON and 400 validation above.

Two module-level helpers do the streaming, so they can be tested without a socket:

- `sse(event: str, data: dict, event_id: int | None = None) -> bytes` →
  `f"event: {event}\ndata: {json.dumps(data)}\n\n"` encoded as UTF-8, preceded by `f"id: {event_id}\n"` when
  `event_id` is given.
- `relay(chunks, wfile, first_id: int = 1) -> str` reads text pieces from the iterator `chunks` and writes
  `sse("delta", {"text": piece}, id)` for each, with ids counting up from `first_id`, flushing after every write. A
  `None` piece means the upstream is still working (a long tool call): write the SSE comment `b": keep-alive\n\n"`
  instead, with no id. When `chunks` is exhausted, write `sse("done", {}, id)` with the next id and return
  `"done"`.
  - The browser left: a write raises `BrokenPipeError` or `ConnectionResetError` → stop reading immediately and
    return `"cancelled"`.
  - The upstream failed: iterating `chunks` raises any other exception → write `sse("error", {"message":
    UNAVAILABLE})` with no id (module constant `"The assistant is unavailable."`; never the exception text, which
    can hold internal details), log the exception server-side with `logging` (`log.exception`), and return
    `"error"`. No `done` event. If writing the error event fails because the browser left, return `"cancelled"`.
  - In every case, call `chunks.close()` if it has one before returning, so a generator wrapping the provider's
    stream closes the upstream connection and the model stops generating for nobody.

`SYSTEM_PROMPT` (module constant) must tell the model it is a support copilot that answers concisely and says
when it does not know.

## Field notes
Demo with the fake model. `make_app` takes the model as a parameter, so a launcher can pass `fde_kit.get_llm()`,
which returns the real client when `FDE_LIVE=1` is set, to show live behavior if the network allows. Rehearse the
failure path: what do you say if the real model is slow? A fake model scripted to raise shows the page's error
message, and on the streaming endpoint the generic `error` event.

Stuck? [HINTS.md](HINTS.md) has three progressive hints and a guide to what each failing test usually means.

## Run and verify

- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository root.
  No API key or network access is needed.
- **Run your work:** from the repository root, `pytest exercises/ch07-full-stack-engineering/ex30-demo-web-ui`.
- **Expected output:** all 16 tests fail against the starter; when you're done, all 16 pass.
- **Check the reference solution:** `pytest --solutions exercises/ch07-full-stack-engineering/ex30-demo-web-ui`: all
  16 pass.
- **Tests:** `test_demo_ui.py` (16 tests).
- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the
  repository root. For a failing test, [HINTS.md](HINTS.md) says what it usually means.
- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference run fails
  too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in the published
  solution, so report it with the repository's Errata issue template.
- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by git.
- **Production caveats:** The replay store lives in one process's memory, and the stream generates the whole answer
  before sending it; a real backend for frontend keeps generated events in a shared store with expiry and lets a
  resumed request follow a generation still in progress. The optional `api_token` is one shared secret, not per-user
  authentication, and the server has no rate limits or per-user cost attribution, which is why it binds to
  `127.0.0.1` only. A production backend for frontend authenticates the user's existing session, reads the provider
  key from a secret store, enforces limits and request ids before any tokens are spent, and logs upstream errors
  server-side while the browser gets only the generic message.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "Demo chat UI served from Python".
Before I write code, teach me building a minimal demo stack with the Python standard library and vanilla JS,
XSS-safe rendering, relaying a streamed answer as server-sent events with cancellation, and how to rehearse failure
paths for a live demo. Use short Python examples that are not the exercise solution. Then ask me three questions
to check my understanding, one at a time, and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/ch07-full-stack-engineering/ex30-demo-web-ui/starter.py so that test_demo_ui.py passes. README.md
in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API: `make_app`,
`sse`, `relay`, `MAX_REPLAYS`. Constraints: Python 3.11+, the standard library and the repo's fde_kit package only (pyyaml is
allowed where the README uses YAML). Do not modify the tests or fde_kit. When you're done, run `pytest
exercises/ch07-full-stack-engineering/ex30-demo-web-ui` and show me the output. If the README and the tests disagree,
stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "Demo chat UI served from Python" as a senior forward deployed engineer would before it ships
to a customer. Specifically: Is there any path where model or user text reaches innerHTML? Does invalid JSON return
a 400 instead of a crash? Would the demo banner be obvious on a projector? Does the stream stop the upstream when
the browser disconnects, and does an upstream error leak its message to the browser? Rank findings by customer
impact, quote the line for each, and say which ones a test should catch.
```
**Production prompt (what this exercise's code sends to a model)**
```text
You are a support copilot for the customer's service desk agents. Answer the agent's question concisely, in at most four sentences, using plain language. If you don't know the answer or it depends on account details you can't see, say so and suggest what the agent should check.
```
