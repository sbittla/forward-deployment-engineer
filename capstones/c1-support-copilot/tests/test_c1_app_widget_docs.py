import importlib
import json
import os
import re
import shutil
import subprocess
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

PACKAGE = "copilot"
HERE = Path(__file__).parent


def post(url, body, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, json.dumps(body).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_http_api(cap, copilot):
    app = importlib.import_module("copilot.app")
    srv = app.make_server(copilot, {"t0k"})
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        with urllib.request.urlopen(base + "/healthz", timeout=5) as r:
            assert json.loads(r.read()) == {"status": "ok"}
        assert post(base + "/v1/ask", {"question": "hi"})[0] == 401
        assert post(base + "/v1/ask", {"q": "x"}, "t0k")[0] == 400
        status, body = post(base + "/v1/ask", {"question": "How many days do I have to file a claim after the loss?"}, "t0k")
        assert status == 200 and "30 days" in body["text"] and body["citations"] == ["claims-process"]
        assert body["request_id"]
    finally:
        srv.shutdown()
        srv.server_close()


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_answer_view_widget(cap_dir):
    env = {**os.environ, "CAP_DIR": str(cap_dir)}
    p = subprocess.run(["node", "--test", str(HERE / "answer_view.test.ts")], capture_output=True, text=True, env=env)
    assert p.returncode == 0, p.stdout + p.stderr


REQUIRED = {
    "discovery_brief.md": ["Problem", "Users", "Success metrics", "Data sources", "Constraints", "Out of scope",
                           "Stakeholders"],
    "runbook.md": ["Overview", "Deploy", "Rollback", "Monitoring", "Re-indexing policy documents", "Escalation"],
}


@pytest.mark.parametrize("name", sorted(REQUIRED))
def test_deliverables(cap_dir, name):
    path = cap_dir / "deliverables" / name
    text = path.read_text(encoding="utf-8")
    headings = [h.strip().lower() for h in re.findall(r"^#+\s+(.*)$", text, re.M)]
    for section in REQUIRED[name]:
        assert any(section.lower() in h for h in headings), f"{name} is missing a '{section}' section"
    assert not re.search(r"TODO|TBD|FIXME", text), f"{name} still has placeholders"
    if name == "discovery_brief.md":
        assert re.search(r"\d+(\.\d+)?\s*(%|min)", text), "success metrics must be quantified"
