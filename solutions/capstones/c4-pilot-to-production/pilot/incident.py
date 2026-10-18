"""Read the pilot's incident log and turn it into findings, each paired with the fix shipped in this service."""
import re

LINE = re.compile(r"^(\S+)\s+(INFO|WARN|ERROR)\s+(.*)$")


def diagnose(lines: list[str]) -> dict:
    events = [m.groups() for m in (LINE.match(l.strip()) for l in lines) if m]
    errors = [e for e in events if e[1] == "ERROR"]
    overload = [e for e in events if "status=529" in e[2]]
    surfaced_500 = [e for e in events if "request failed" in e[2] and "status=500" in e[2]]
    slow = [e for e in events if (m := re.search(r"duration_ms=(\d+)", e[2])) and int(m.group(1)) >= 30000]
    backlog = [int(m.group(1)) for e in events if (m := re.search(r"backlog depth=(\d+)", e[2]))]
    probe = [e for e in events if "liveness probe failed" in e[2]]

    findings = []
    if overload:
        findings.append({"finding": f"{len(overload)} upstream 529 overloads were not retried; "
                                    f"{len(surfaced_500)} surfaced to users as HTTP 500",
                         "fix": "retries with backoff plus a fallback model (ResilientLLM)"})
    if slow:
        findings.append({"finding": f"{len(slow)} requests took 30 s or longer (no client timeout)",
                         "fix": "explicit timeout and circuit breaker; 503 with Retry-After when open"})
    if backlog:
        findings.append({"finding": f"request backlog reached {max(backlog)} on a single-threaded server",
                         "fix": "threaded server, horizontal scaling (HPA) and capacity plan from the load test"})
    if probe:
        findings.append({"finding": "the container was restarted by a liveness probe because /healthz did not exist",
                         "fix": "/healthz (liveness) and /readyz (readiness that reflects the LLM circuit)"})
    return {
        "first_error": errors[0][0] if errors else None,
        "error_count": len(errors),
        "findings": findings,
    }
