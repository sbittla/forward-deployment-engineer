"""Customer-environment preflight: run on site before go-live, send the output to the FDE."""
import os
import socket
from urllib.parse import urlsplit

from .config import ConfigError, load_settings


def run_preflight(env, resolve=socket.gethostbyname, connect=None, path_exists=os.path.exists) -> dict:
    """Return {"status": PASS|WARN|FAIL, "checks": [(name, status, detail)]}."""
    raise NotImplementedError


if __name__ == "__main__":
    import sys

    report = run_preflight(os.environ)
    for name, status, detail in report["checks"]:
        print(f"[{status}] {name}: {detail}")
    print(f"Overall: {report['status']}")
    sys.exit({"PASS": 0, "WARN": 1, "FAIL": 2}[report["status"]])
