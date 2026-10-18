"""Run every exercise and capstone test, Python and TypeScript, against starters or reference solutions.

usage:
  python scripts/check.py               # your work (starters); red until you solve them
  python scripts/check.py --solutions   # reference solutions; must be all green
  python scripts/check.py --solutions exercises/m07-retrieval-rag   # one module
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str]) -> int:
    solutions = "--solutions" in argv
    targets = [a for a in argv if not a.startswith("--")] or ["exercises", "capstones"]
    py = [sys.executable, "-m", "pytest", "-q", *targets] + (["--solutions"] if solutions else [])
    rc = subprocess.call(py, cwd=ROOT)

    ts_tests = sorted(p for t in targets for p in (ROOT / t).rglob("*.test.ts") if "capstones" not in p.parts)
    if ts_tests and shutil.which("node"):
        env = {**os.environ, **({"FDE_SOLUTIONS": "1"} if solutions else {})}
        for t in ts_tests:
            print(f"node --test {t.relative_to(ROOT)}")
            rc |= subprocess.call(["node", "--test", str(t)], cwd=ROOT, env=env)
    elif ts_tests:
        print("node not found: skipping TypeScript exercises (needs Node >= 23.6)")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
