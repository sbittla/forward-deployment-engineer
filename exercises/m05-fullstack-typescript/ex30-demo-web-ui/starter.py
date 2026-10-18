from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SYSTEM_PROMPT = ""


def make_app(llm, demo_mode: bool = True) -> ThreadingHTTPServer:
    raise NotImplementedError
