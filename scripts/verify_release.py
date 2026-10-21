"""Verify a published release from a clean, anonymous checkout and write a test report.

Clones the public repository over HTTPS with no credentials, checks out the given ref (a tag or commit), installs the
documented requirements into a fresh virtual environment, and runs the documented checks: every reference solution
and the three linters (`check.py --solutions`), every starter red (`starters_red.py`), and, with `--docker`, every
suite one at a time in the Docker runner (`run_all.py --docker`). The report records the commit, OS, tool versions,
each command, its exit code and the summary line it printed.

usage: python scripts/verify_release.py <ref> [--docker] [--repo URL] [--report PATH]
"""
import argparse
import datetime
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

REPO = "https://github.com/sbittla/forward-deployment-engineer.git"


def run(cmd: list[str], cwd: Path, env: dict, log: Path) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log.write_text(p.stdout + p.stderr, encoding="utf-8")
    tail = [line for line in (p.stdout + p.stderr).splitlines() if line.strip()]
    return p.returncode, tail[-1] if tail else ""


def version(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout.strip().splitlines()[0]
    except (OSError, IndexError, subprocess.TimeoutExpired):
        return "not available"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ref")
    ap.add_argument("--docker", action="store_true")
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--report", default="release-verification.md")
    args = ap.parse_args()

    work = Path(tempfile.mkdtemp(prefix="fde-verify-"))
    logs = work / "logs"
    logs.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GH_", "GITHUB_"))}
    env.update(GIT_TERMINAL_PROMPT="0", GIT_ASKPASS="", GCM_INTERACTIVE="never", PYTHONDONTWRITEBYTECODE="1")
    src = work / "repo"
    steps = []

    # anonymous clone: no credential helper, no prompts
    rc, line = run(["git", "-c", "credential.helper=", "clone", "--quiet", args.repo, str(src)], work, env,
                   logs / "clone.log")
    steps.append(("Anonymous clone over HTTPS", f"git clone {args.repo}", rc, line or "cloned"))
    if rc:
        return report(args, work, steps, "", fail=True)
    rc, line = run(["git", "-c", "advice.detachedHead=false", "checkout", "--quiet", args.ref], src, env,
                   logs / "checkout.log")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=src, capture_output=True, text=True).stdout.strip()
    steps.append((f"Check out {args.ref}", f"git checkout {args.ref}", rc, commit))
    if rc:
        return report(args, work, steps, commit, fail=True)

    venv.create(work / "venv", with_pip=True)
    py = str(work / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python"))
    checks = [
        ("Install documented requirements", [py, "-m", "pip", "install", "--quiet", "-r", "requirements.txt"]),
        ("All reference solutions and linters", [py, "scripts/check.py", "--solutions"]),
        ("Every starter fails at least one test", [py, "scripts/starters_red.py"]),
    ]
    if args.docker:
        checks.append(("Every suite in Docker, checked one at a time", [py, "scripts/run_all.py", "--docker"]))
    for title, cmd in checks:
        rc, line = run(cmd, src, env, logs / f"{len(steps)}.log")
        shown = " ".join(["python"] + cmd[1:]) if cmd[0] == py else " ".join(cmd)
        steps.append((title, shown, rc, line))
    summary = src / "output" / "summary.md"
    if summary.exists():
        shutil.copy(summary, work / "summary.md")
    return report(args, work, steps, commit, fail=any(s[2] for s in steps))


def report(args, work: Path, steps: list, commit: str, fail: bool) -> int:
    when = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Release verification: {args.ref}", "",
             f"**Result: {'FAIL' if fail else 'PASS'}** · {when}", "",
             "| Item | Value |", "|---|---|",
             f"| Repository | `{args.repo}` (anonymous HTTPS clone, no credentials) |",
             f"| Ref | `{args.ref}` → commit `{commit or 'n/a'}` |",
             f"| OS | {platform.platform()} |",
             f"| Python | {sys.version.split()[0]} |",
             f"| Node.js | {version(['node', '--version'])} |",
             f"| Docker | {version(['docker', '--version']) if args.docker else 'not used'} |",
             "", "| Step | Command | Exit | Result |", "|---|---|---|---|"]
    for title, cmd, rc, line in steps:
        lines.append(f"| {title} | `{cmd}` | {rc} | {line.replace('|', '/')} |")
    docker_summary = work / "summary.md"
    if docker_summary.exists():
        first = [line for line in docker_summary.read_text(encoding="utf-8").splitlines() if line.strip()][:2]
        lines += ["", "Docker run summary: " + " — ".join(first)]
    lines += ["", f"Logs: `{work / 'logs'}`"]
    Path(args.report).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
