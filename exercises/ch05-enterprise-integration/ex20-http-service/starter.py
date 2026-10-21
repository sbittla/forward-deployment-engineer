from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MAX_BODY = 65536
MAX_QUESTION = 2000


def make_server(answer_fn, tokens, host="127.0.0.1", port=0) -> ThreadingHTTPServer:
    raise NotImplementedError
