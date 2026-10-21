from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SYSTEM_PROMPT = ""
UNAVAILABLE = "The assistant is unavailable."
MAX_BODY_BYTES = 64 * 1024


def sse(event: str, data: dict) -> bytes:
    raise NotImplementedError


def relay(chunks, wfile) -> str:
    raise NotImplementedError


def make_app(llm, demo_mode: bool = True, api_token: str | None = None) -> ThreadingHTTPServer:
    raise NotImplementedError
