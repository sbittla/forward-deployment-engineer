"""Check that every exercise and capstone starts red: its tests must fail against the starter code.

usage: python scripts/starters_red.py
Runs pytest once over the starters, then reports any exercise directory in which no test failed. A starter that
already passes its whole suite teaches nothing, and usually means a test lost its assertion.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def python_suites() -> dict[str, list[bool]]:
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "report.xml"
        subprocess.call([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "exercises", "capstones",
                         f"--junitxml={report}"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        suites: dict[str, list[bool]] = defaultdict(list)
        for case in ET.parse(report).iter("testcase"):
            parts = case.get("classname", "").split(".")
            suite = "/".join(parts[:3] if parts[0] == "exercises" else parts[:2])
            failed = case.find("failure") is not None or case.find("error") is not None
            suites[suite].append(failed)
        return suites


def ts_suites() -> dict[str, list[bool]]:
    if not shutil.which("node"):
        print("node not found: skipping TypeScript starters")
        return {}
    env = {k: v for k, v in os.environ.items() if k != "FDE_SOLUTIONS"}
    out = {}
    for test in sorted((ROOT / "exercises").rglob("*.test.ts")):
        rc = subprocess.call(["node", "--test", str(test)], cwd=ROOT, env=env,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        out[test.parent.relative_to(ROOT).as_posix()] = [rc != 0]
    return out


def main() -> int:
    suites = {**python_suites(), **ts_suites()}
    green = sorted(name for name, results in suites.items() if not any(results))
    for name in green:
        print(f"starter already passes every test: {name}")
    print(f"starters-red: {len(suites)} suites checked, {len(green)} problem(s)")
    return 1 if green or not suites else 0


if __name__ == "__main__":
    sys.exit(main())
