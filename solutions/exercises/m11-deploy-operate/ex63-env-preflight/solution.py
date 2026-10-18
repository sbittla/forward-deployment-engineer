import os
import shutil
import socket
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Check:
    name: str
    fn: Callable[[], tuple[bool, str]]
    severity: str = "fail"
    hint: str = ""


@dataclass
class Report:
    results: list[tuple[Check, bool, str]] = field(default_factory=list)

    @property
    def status(self) -> str:
        failed = [c.severity for c, ok, _ in self.results if not ok]
        if "fail" in failed:
            return "FAIL"
        return "WARN" if failed else "PASS"

    @property
    def exit_code(self) -> int:
        return {"PASS": 0, "WARN": 1, "FAIL": 2}[self.status]

    def render(self) -> str:
        lines = []
        for c, ok, detail in self.results:
            label = "PASS" if ok else c.severity.upper()
            hint = f" (hint: {c.hint})" if not ok and c.hint else ""
            lines.append(f"[{label}] {c.name} — {detail}{hint}")
        lines.append(f"Overall: {self.status}")
        return "\n".join(lines)


def _v(t) -> str:
    return ".".join(str(x) for x in t)


def python_version(min_version, current=sys.version_info[:3], severity="fail", hint="") -> Check:
    def fn():
        ok = tuple(current) >= tuple(min_version)
        return ok, f"{_v(current)} {'>=' if ok else '<'} {_v(min_version)}"
    return Check("python_version", fn, severity, hint)


def env_vars(names, env, severity="fail", hint="") -> Check:
    def fn():
        missing = [n for n in names if not env.get(n)]
        return not missing, f"missing: {', '.join(missing)}" if missing else "all set"
    return Check("env_vars", fn, severity, hint)


def disk_free(path, min_gb, usage=shutil.disk_usage, severity="fail", hint="") -> Check:
    def fn():
        free_gb = usage(path).free / 1e9
        return free_gb >= min_gb, f"{free_gb:.1f} GB free"
    return Check(f"disk_free({path})", fn, severity, hint)


def dns(host, resolve=socket.gethostbyname, severity="fail", hint="") -> Check:
    def fn():
        try:
            return True, f"{host} -> {resolve(host)}"
        except Exception as exc:
            return False, type(exc).__name__
    return Check(f"dns({host})", fn, severity, hint)


def tcp(host, port, connect, severity="fail", hint="") -> Check:
    def fn():
        try:
            connect(host, port)
            return True, "connected"
        except Exception as exc:
            return False, type(exc).__name__
    return Check(f"tcp({host}:{port})", fn, severity, hint)


def clock_skew(reference_epoch, max_skew_s=60, now=time.time, severity="warn", hint="") -> Check:
    def fn():
        skew = int(abs(now() - reference_epoch))
        return skew <= max_skew_s, f"skew {skew}s"
    return Check("clock_skew", fn, severity, hint)


def writable(path, severity="fail", hint="") -> Check:
    def fn():
        fd, name = tempfile.mkstemp(dir=path)
        os.close(fd)
        os.remove(name)
        return True, "writable"
    return Check(f"writable({path})", fn, severity, hint)


def run_preflight(checks: list[Check]) -> Report:
    rep = Report()
    for c in checks:
        try:
            ok, detail = c.fn()
        except Exception as exc:
            ok, detail = False, type(exc).__name__
        rep.results.append((c, ok, detail))
    return rep
