import hmac
import json
import logging
import re
import threading
import time
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SYSTEM_PROMPT = (
    "You are a customer-support copilot for the customer's agents. Answer concisely and cite the source "
    "when you have one. If you do not know the answer, say you don't know instead of guessing."
)

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Support Copilot</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; }
  #log div { margin: .5rem 0; padding: .5rem .75rem; border-radius: 8px; white-space: pre-wrap; }
  .user { background: #e8f0fe; } .assistant { background: #f1f3f4; } .error { background: #fde7e9; }
  form { display: flex; gap: .5rem; } input { flex: 1; padding: .5rem; }
</style>
</head>
<body>
<h1>Support Copilot</h1>
__BANNER__
<div id="log"></div>
<form id="chat-form">
  <input name="q" autocomplete="off" placeholder="Ask about a policy..." required>
  <button type="submit">Send</button>
</form>
<script>
  const log = document.getElementById("log");
  const form = document.getElementById("chat-form");
  const history = [];
  function add(role, text) {
    const div = document.createElement("div");
    div.className = role;
    div.textContent = text;
    log.appendChild(div);
    return div;
  }
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const q = form.q.value.trim();
    if (!q) return;
    form.q.value = "";
    add("user", q);
    const pending = add("assistant", "...");
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ q, history }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || res.status);
      pending.textContent = data.answer;
      history.push({ role: "user", content: q }, { role: "assistant", content: data.answer });
    } catch (err) {
      pending.className = "error";
      pending.textContent = "Something went wrong: " + err.message;
    }
  });
</script>
</body>
</html>
"""
BANNER = ('<p id="demo-banner" style="background:#fff3cd;border:1px solid #e0c060;padding:.5rem;border-radius:6px">'
          'DEMO MODE: answers come from a scripted model, not a live LLM.</p>')


UNAVAILABLE = "The assistant is unavailable."
MAX_BODY_BYTES = 64 * 1024


MAX_REPLAYS = 256
log = logging.getLogger("ex30.bff")


def sse(event: str, data: dict, event_id: int | None = None) -> bytes:
    head = f"id: {event_id}\n" if event_id is not None else ""
    return f"{head}event: {event}\ndata: {json.dumps(data)}\n\n".encode()


def relay(chunks, wfile, first_id: int = 1) -> str:
    """Relay text deltas to the browser as SSE with numbered ids; close the upstream if the browser leaves."""
    next_id = first_id
    try:
        for text in chunks:  # None means "still working": send a comment so proxies keep the connection open
            if text is None:
                wfile.write(b": keep-alive\n\n")
            else:
                wfile.write(sse("delta", {"text": text}, next_id))
                next_id += 1
            wfile.flush()
        wfile.write(sse("done", {}, next_id))
        wfile.flush()
        return "done"
    except (BrokenPipeError, ConnectionResetError):
        return "cancelled"
    except Exception:
        log.exception("upstream stream failed")  # details stay in the server log, never in the browser
        try:
            wfile.write(sse("error", {"message": UNAVAILABLE}))
            wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            return "cancelled"
        return "error"
    finally:
        close = getattr(chunks, "close", None)
        if close is not None:
            close()


def _valid_history(h):
    return isinstance(h, list) and all(
        isinstance(m, dict) and m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str) for m in h)


def make_app(llm, demo_mode: bool = True, api_token: str | None = None) -> ThreadingHTTPServer:
    page = PAGE.replace("__BANNER__", BANNER if demo_mode else "").encode()
    replays: OrderedDict = OrderedDict()  # (Authorization, request_id) -> answer pieces, for Last-Event-ID resume
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _send(self, status, body: bytes, ctype="application/json"):
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status, obj):
            self._send(status, json.dumps(obj).encode())

        def do_GET(self):
            if self.path == "/":
                return self._send(200, page, "text/html; charset=utf-8")
            self._json(404, {"error": "not found"})

        def do_POST(self):
            if self.path not in ("/api/chat", "/api/chat/stream"):
                return self._json(404, {"error": "not found"})
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                length = -1
            if not 0 <= length <= MAX_BODY_BYTES:  # refused before reading: the size is the client's claim
                self.close_connection = True
                return self._json(413, {"error": "body too large"})
            raw = self.rfile.read(length)
            if api_token is not None:  # checked before the body is parsed or any tokens are spent
                given = self.headers.get("Authorization", "")
                if not hmac.compare_digest(given.encode(), f"Bearer {api_token}".encode()):
                    return self._json(401, {"error": "unauthorized"})
            try:
                body = json.loads(raw)
            except (json.JSONDecodeError, UnicodeDecodeError):
                return self._json(400, {"error": "body must be JSON"})
            q = body.get("q") if isinstance(body, dict) else None
            history = body.get("history", []) if isinstance(body, dict) else None
            request_id = body.get("request_id") if isinstance(body, dict) else None
            if not isinstance(q, str) or not q.strip() or not _valid_history(history):
                return self._json(400, {"error": "need non-empty q and a valid history list"})
            if request_id is not None and not (isinstance(request_id, str) and 0 < len(request_id) <= 128):
                return self._json(400, {"error": "request_id must be a string of 1 to 128 characters"})
            messages = history + [{"role": "user", "content": q}]
            if self.path == "/api/chat/stream":
                return self._stream(messages, request_id)
            t0 = time.perf_counter()
            resp = llm.complete(messages, system=SYSTEM_PROMPT)
            self._json(200, {"answer": resp.text, "model": resp.model,
                             "latency_ms": int((time.perf_counter() - t0) * 1000)})

        def _stream(self, messages, request_id):
            last = self.headers.get("Last-Event-ID", "")
            if last and not re.fullmatch(r"[0-9]{1,9}", last):
                return self._json(400, {"error": "bad Last-Event-ID"})
            key = (self.headers.get("Authorization", ""), request_id)  # a caller can replay only its own answer
            with lock:
                kept = replays.get(key) if request_id else None
            if last and kept is None:  # regenerating would send a different answer after the old one's start
                return self._json(409, {"error": "cannot resume this stream"})
            skip = int(last or 0)

            def chunks():
                text = llm.complete(messages, system=SYSTEM_PROMPT).text
                pieces = re.findall(r"\S+\s*|\s+", text)
                if request_id:
                    with lock:
                        replays[key] = pieces
                        while len(replays) > MAX_REPLAYS:
                            replays.popitem(last=False)
                yield from pieces

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            relay(iter(kept[skip:]) if kept is not None else chunks(), self.wfile, first_id=skip + 1)
            self.close_connection = True

    return ThreadingHTTPServer(("127.0.0.1", 0), Handler)
