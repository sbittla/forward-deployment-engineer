"""Customer-environment preflight: run on site before go-live, send the output to the FDE."""
import os
import socket
from urllib.parse import urlsplit

from .config import ConfigError, load_settings


def run_preflight(env, resolve=socket.gethostbyname, connect=None, path_exists=os.path.exists) -> dict:
    """Return {"status": PASS|WARN|FAIL, "checks": [(name, status, detail)]}."""
    checks = []

    def add(name, status, detail):
        checks.append((name, status, detail))

    try:
        settings = load_settings(env)
        add("config", "PASS", "settings valid")
    except ConfigError as e:
        add("config", "FAIL", "; ".join(e.errors))
        settings = None

    if settings:
        host = urlsplit(settings.llm_endpoint).hostname
        try:
            resolve(host)
            add("dns", "PASS", f"{host} resolves")
        except Exception as exc:
            add("dns", "FAIL", f"{host}: {type(exc).__name__}")
        if connect is not None:
            try:
                connect(settings.https_proxy or host, 443)
                add("egress", "PASS", "via proxy" if settings.https_proxy else "direct")
            except Exception as exc:
                add("egress", "FAIL", type(exc).__name__)
        if not settings.egress_allowlist:
            add("allowlist", "WARN", "PILOT_EGRESS_ALLOWLIST empty: egress is not restricted")
        else:
            add("allowlist", "PASS", ", ".join(settings.egress_allowlist))
        if settings.ca_bundle and not path_exists(settings.ca_bundle):
            add("ca_bundle", "FAIL", f"{settings.ca_bundle} not found")
        elif settings.https_proxy and not settings.ca_bundle:
            add("ca_bundle", "WARN", "proxy set but no corporate CA bundle: TLS interception will fail")
        else:
            add("ca_bundle", "PASS", settings.ca_bundle or "system default")

    statuses = [s for _, s, _ in checks]
    overall = "FAIL" if "FAIL" in statuses else "WARN" if "WARN" in statuses else "PASS"
    return {"status": overall, "checks": checks}


if __name__ == "__main__":
    import sys

    report = run_preflight(os.environ)
    for name, status, detail in report["checks"]:
        print(f"[{status}] {name}: {detail}")
    print(f"Overall: {report['status']}")
    sys.exit({"PASS": 0, "WARN": 1, "FAIL": 2}[report["status"]])
