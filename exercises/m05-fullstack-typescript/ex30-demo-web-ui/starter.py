from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SYSTEM_PROMPT = ""
UNAVAILABLE = "The assistant is unavailable."


def sse(event: str, data: dict) -> bytes:
    raise NotImplementedError


def relay(chunks, wfile) -> str:
    raise NotImplementedError


def make_app(llm, demo_mode: bool = True) -> ThreadingHTTPServer:
    raise NotImplementedError
