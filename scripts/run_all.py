"""Run every exercise and capstone reference solution, analyse the results, and write them to output/.

usage:
  python scripts/run_all.py --docker            # build docker/runner.Dockerfile, run inside it with --gpus all
  python scripts/run_all.py                     # run in the current environment
  python scripts/run_all.py --jobs 8 ex31 c2    # only suites whose path contains ex31 or c2
  python scripts/run_all.py --no-starters       # skip the starter cross-check

output/ mirrors the course tree and is rewritten on every full run:
  output/summary.md, summary.json, environment.txt (Python, Node, GPU), lints/<lint>.log
  output/exercises/<module>/<exercise>/result.json, pytest.log, node.log
  output/capstones/<capstone>/result.json, pytest.log

A suite is expected to pass only if all of these hold:
  - every test it ran against the reference solution passed: no failures, errors or skips
  - every test declared in its test files (def test_* / test("...")) actually ran: none silently uncollected
  - the starter fails at least one of those tests: the suite really checks the work (skip with --no-starters)
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
IMAGE = "fde-runner:latest"
PY_TEST = re.compile(r"^(?:async )?def (test_\w+)", re.M)
TS_TEST = re.compile(r"""^\s*(?:test|it)\(\s*(["'`])(.+?)\1""", re.M)


def discover(filters: list[str]) -> list[dict]:
    suites = []
    for d in sorted((ROOT / "exercises").glob("m*/ex*")) + sorted((ROOT / "capstones").glob("c*")):
        rel = d.relative_to(ROOT).as_posix()
        if not d.is_dir() or (filters and not any(f in rel for f in filters)):
            continue
        py = sorted(d.rglob("test_*.py"))
        # capstone TypeScript tests are driven by their pytest suite; exercise ones are run with node directly
        ts = [] if d.parts[-2] == "capstones" else sorted(d.glob("*.test.ts"))
        declared = {f"py:{n}" for f in py for n in PY_TEST.findall(f.read_text(encoding="utf-8"))}
        declared |= {f"ts:{m[1]}" for f in ts for m in TS_TEST.findall(f.read_text(encoding="utf-8"))}
        suites.append({"path": rel, "py": bool(py), "ts": [t.relative_to(ROOT).as_posix() for t in ts],
                       "declared": sorted(declared)})
    return suites


def junit_cases(xml: Path, prefix: str) -> list[dict]:
    cases = []
    for case in ET.parse(xml).iter("testcase"):
        status = "passed"
        for tag, name in (("failure", "failed"), ("error", "error"), ("skipped", "skipped")):
            node = case.find(tag)
            if node is not None:
                status = name
                msg = (node.get("message") or node.text or "").strip()
                break
        c = {"test": f"{prefix}:{case.get('name')}", "status": status}
        if status != "passed":
            c["message"] = msg[:500]
        cases.append(c)
    return cases


def run_tests(s: dict, outdir: Path | None, solutions: bool) -> tuple[list[dict], int]:
    """Run one suite; return its test cases and the combined exit code. Logs go to outdir when given."""
    cases, rc = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        if s["py"]:
            xml = tmp / "pytest.xml"
            cmd = [sys.executable, "-m", "pytest", "-q", "-rfEs", "-p", "no:cacheprovider", s["path"],
                   f"--junitxml={xml}"] + (["--solutions"] if solutions else [])
            p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            rc |= p.returncode
            if outdir:
                (outdir / "pytest.log").write_text(p.stdout + p.stderr, encoding="utf-8")
            cases += junit_cases(xml, "py") if xml.exists() else [{"test": "py:<collection>", "status": "error"}]
        env = {k: v for k, v in os.environ.items() if k != "FDE_SOLUTIONS"}
        if solutions:
            env["FDE_SOLUTIONS"] = "1"
        logs = []
        for i, t in enumerate(s["ts"]):
            if not shutil.which("node"):
                cases.append({"test": f"ts:{t}", "status": "skipped", "message": "node not installed"})
                continue
            xml = tmp / f"node{i}.xml"
            p = subprocess.run(["node", "--test", "--test-reporter=spec", "--test-reporter-destination=stdout",
                                "--test-reporter=junit", f"--test-reporter-destination={xml}", t],
                               cwd=ROOT, env=env, capture_output=True, text=True)
            rc |= p.returncode
            logs.append(f"$ node --test {t}\n{p.stdout}{p.stderr}")
            cases += junit_cases(xml, "ts") if xml.exists() else [{"test": f"ts:{t}", "status": "error"}]
        if outdir and logs:
            (outdir / "node.log").write_text("\n".join(logs), encoding="utf-8")
    return cases, rc


def analyse(s: dict, cases: list[dict], rc: int, starter: list[dict] | None) -> dict:
    ran = {re.sub(r"\[.*\]$", "", c["test"]) for c in cases}  # parametrized ids collapse to the declared name
    counts = {k: sum(c["status"] == k for c in cases) for k in ("passed", "failed", "error", "skipped")}
    problems = []
    if counts["failed"] or counts["error"]:
        problems.append(f"{counts['failed']} failed, {counts['error']} errors against the solution")
    if counts["skipped"]:
        problems.append(f"{counts['skipped']} skipped")
    if rc and not (counts["failed"] or counts["error"]):
        problems.append(f"test runner exited {rc} although no test failed")
    if not cases:
        problems.append("no tests ran")
    missing = sorted(set(s["declared"]) - ran)
    if missing:
        problems.append(f"declared but never ran: {', '.join(missing)}")
    red = None
    if starter is not None:
        red = sum(c["status"] in ("failed", "error") for c in starter)
        if red == 0:
            problems.append("starter passes every test: the suite does not discriminate")
    return {"path": s["path"], "status": "FAIL" if problems else "PASS", "problems": problems,
            "tests": counts, "declared": len(s["declared"]), "ran": len(cases),
            "starter_failing": red, "cases": cases}


def run_suite(s: dict, check_starters: bool) -> dict:
    outdir = OUT / s["path"]
    outdir.mkdir(parents=True, exist_ok=True)
    cases, rc = run_tests(s, outdir, solutions=True)
    starter = run_tests(s, None, solutions=False)[0] if check_starters else None
    res = analyse(s, cases, rc, starter)
    (outdir / "result.json").write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    return res


def run_lint(script: str) -> dict:
    p = subprocess.run([sys.executable, f"scripts/{script}.py"], cwd=ROOT, capture_output=True, text=True)
    (OUT / "lints").mkdir(exist_ok=True)
    (OUT / "lints" / f"{script}.log").write_text(p.stdout + p.stderr, encoding="utf-8")
    return {"name": script, "status": "PASS" if p.returncode == 0 else "FAIL"}


def capture(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout.strip() or "(no output)"
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"unavailable: {e}"


def write_environment() -> None:
    lines = [f"python: {sys.version.split()[0]} ({sys.executable})",
             f"node: {capture(['node', '--version']) if shutil.which('node') else 'not installed'}",
             f"platform: {sys.platform}", f"in docker: {Path('/.dockerenv').exists()}",
             "", "nvidia-smi:", capture(["nvidia-smi"]) if shutil.which("nvidia-smi") else "not available"]
    (OUT / "environment.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(results: list[dict], lints: list[dict], seconds: float, check_starters: bool) -> bool:
    bad = [r for r in results if r["status"] != "PASS"] + [lint for lint in lints if lint["status"] != "PASS"]
    totals = {k: sum(r["tests"][k] for r in results) for k in ("passed", "failed", "error", "skipped")}
    summary = {"ok": not bad, "seconds": round(seconds, 1), "suites": len(results),
               "suites_passed": sum(r["status"] == "PASS" for r in results), "tests": totals,
               "starters_checked": check_starters, "lints": lints,
               "suites_detail": [{k: v for k, v in r.items() if k != "cases"} for r in results]}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    md = [f"# Solutions run: {'ALL PASS' if not bad else f'{len(bad)} NOT PASSING'}", "",
          f"Suites {summary['suites_passed']}/{len(results)} as expected · tests {totals['passed']} passed, "
          f"{totals['failed']} failed, {totals['error']} errors, {totals['skipped']} skipped · {summary['seconds']}s",
          "", "Expected = every declared test ran and passed against the reference solution"
          + (", and the starter fails at least one." if check_starters else "."),
          "Environment: environment.txt. Per suite: <path>/result.json (every test case), pytest.log, node.log.", ""]
    if bad:
        md += ["## Not as expected", ""]
        md += [f"- **{r.get('path', r['name'])}**: {'; '.join(r.get('problems', ['lint failed']))}" for r in bad] + [""]
    md += ["## Suites", "", "| Suite | Status | Declared | Ran | Passed | Failed | Errors | Skipped | Starter failing |",
           "|---|---|---|---|---|---|---|---|---|"]
    md += [f"| [{r['path']}]({r['path']}/result.json) | {r['status']} | {r['declared']} | {r['ran']} | "
           f"{r['tests']['passed']} | {r['tests']['failed']} | {r['tests']['error']} | {r['tests']['skipped']} | "
           f"{'n/a' if r['starter_failing'] is None else r['starter_failing']} |" for r in results]
    md += ["", "## Lints", ""] + [f"- {lint['name']}: {lint['status']} (lints/{lint['name']}.log)" for lint in lints]
    (OUT / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return not bad


def run_in_docker(argv: list[str]) -> int:
    if not shutil.which("docker"):
        raise SystemExit("docker not found")
    rc = subprocess.call(["docker", "build", "-t", IMAGE, "-f", str(ROOT / "docker" / "runner.Dockerfile"), str(ROOT)])
    if rc:
        return rc
    inner = [a for a in argv if a != "--docker"]
    return subprocess.call(["docker", "run", "--rm", "--gpus", "all", "-e", "PYTHONDONTWRITEBYTECODE=1",
                            "-v", f"{ROOT}:/work", "-w", "/work", IMAGE, "python3", "scripts/run_all.py", *inner])


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("filters", nargs="*", help="only run suites whose path contains one of these")
    ap.add_argument("--docker", action="store_true", help="run inside the runner image with --gpus all")
    ap.add_argument("--no-starters", action="store_true", help="skip checking that each starter fails")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4, help="suites to run in parallel")
    args = ap.parse_args(argv)
    if args.docker:
        return run_in_docker(argv)

    if not args.filters:  # a full run replaces the whole report; a filtered run updates only its suites
        for p in ("exercises", "capstones", "lints"):
            shutil.rmtree(OUT / p, ignore_errors=True)
    OUT.mkdir(exist_ok=True)
    write_environment()
    suites = discover(args.filters)
    start = time.monotonic()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(lambda s: run_suite(s, not args.no_starters), suites))
    for r in results:
        starter = "" if r["starter_failing"] is None else f", starter fails {r['starter_failing']}"
        problems = f"  <- {'; '.join(r['problems'])}" if r["problems"] else ""
        print(f"{r['status']:4}  {r['path']}  ({r['ran']} ran / {r['declared']} declared, "
              f"{r['tests']['passed']} passed{starter}){problems}")
    if args.filters:
        ok = all(r["status"] == "PASS" for r in results)
        print(f"\n{'ALL PASS' if ok else 'NOT ALL PASSING'} (filtered run: summary.md not rewritten)")
        return 0 if ok else 1
    lints = [run_lint(s) for s in ("spec_lint", "hints_lint")]
    ok = write_report(results, lints, time.monotonic() - start, not args.no_starters)
    print(f"\n{'ALL PASS' if ok else 'NOT ALL PASSING'}: report in output/summary.md")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
