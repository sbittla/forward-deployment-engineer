"""The pilot as the customer runs it today. Read it; don't run it. Everything wrong with it is on purpose."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

import anthropic

client = anthropic.Anthropic(api_key="sk-EXAMPLE-NOT-A-REAL-KEY")   # hardcoded secret


class H(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        print("summarizing", body)                                       # logs customer data to stdout
        msg = client.messages.create(                                     # no timeout, no retry, no fallback
            model="claude-opus-5-5", max_tokens=1024,
            messages=[{"role": "user", "content": "Summarize: " + body["text"]}])
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"summary": msg.content[0].text}).encode())


HTTPServer(("0.0.0.0", 8080), H).serve_forever()                         # single-threaded, no auth, no health check
