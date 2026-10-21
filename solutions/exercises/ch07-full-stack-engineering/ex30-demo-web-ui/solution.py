import hmac
import json
import re
import time
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


def sse(event: str, data: dict) -> bytes:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n".encode()


def relay(chunks, wfile) -> str:
    """Relay text deltas to the browser as SSE; close the upstream if the browser leaves."""
    try:
        for text in chunks:  # None means "still working": send a comment so proxies keep the connection open
            wfile.write(b": keep-alive\n\n" if text is None else sse("delta", {"text": text}))
            wfile.flush()
        wfile.write(sse("done", {}))
        wfile.flush()
        return "done"
    except (BrokenPipeError, ConnectionResetError):
        return "cancelled"
    except Exception:
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
            if not isinstance(q, str) or not q.strip() or not _valid_history(history):
                return self._json(400, {"error": "need non-empty q and a valid history list"})
            messages = history + [{"role": "user", "content": q}]
            if self.path == "/api/chat/stream":
                return self._stream(messages)
            t0 = time.perf_counter()
            resp = llm.complete(messages, system=SYSTEM_PROMPT)
            self._json(200, {"answer": resp.text, "model": resp.model,
                             "latency_ms": int((time.perf_counter() - t0) * 1000)})

        def _stream(self, messages):
            def chunks():
                text = llm.complete(messages, system=SYSTEM_PROMPT).text
                yield from re.findall(r"\S+\s*|\s+", text)

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            relay(chunks(), self.wfile)
            self.close_connection = True

    return ThreadingHTTPServer(("127.0.0.1", 0), Handler)
