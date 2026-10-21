"""Run every exercise and capstone test, Python and TypeScript, against starters or reference solutions.

usage:
  python scripts/check.py               # your work (starters); red until you solve them
  python scripts/check.py --solutions   # reference solutions (+ spec lint); must be all green
  python scripts/check.py --solutions exercises/ch10-rag   # one chapter folder
  python scripts/check.py --solutions --chapter 10   # the same, by chapter number
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The book's chapters and the exercises each one teaches (Appendix G of the book has the same table).
CHAPTERS = {
    2: [1, 2, 3, 4, 6, 7, 8, 81], 3: [5, 68, 69, 82, 84], 4: list(range(9, 16)),
    5: [16, 17, 18, 19, 20, 21, 78], 6: [22, 23, 24, 25, 26, 77, 80, 92], 7: [27, 28, 29, 30, 91],
    8: [95, 96, 97, 98], 9: [31, 32, 33, 34, 35, 36, 86], 10: [37, 38, 39, 40, 41, 88],
    11: [42, 43, 44, 45, 46, 47, 48, 79, 85], 12: [49, 50, 51, 52, 99, 100],
    13: [53, 54, 55, 56, 83, 89, 93], 14: [57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 76, 94],
    15: [67, 70, 71, 72, 73, 74, 75, 87], 16: [90],
}


def chapter_targets(chapter: int) -> list[str]:
    if chapter not in CHAPTERS:
        raise SystemExit(f"chapter {chapter} has no exercises; chapters with exercises: {sorted(CHAPTERS)}")
    dirs = []
    for n in CHAPTERS[chapter]:
        found = sorted((ROOT / "exercises").glob(f"ch{chapter:02d}-*/ex{n:02d}-*"))
        if len(found) != 1:
            raise SystemExit(f"expected one directory for ex{n:02d}, found {len(found)}")
        dirs.append(found[0].relative_to(ROOT).as_posix())
    return dirs


def main(argv: list[str]) -> int:
    solutions = "--solutions" in argv
    if "--chapter" in argv:
        i = argv.index("--chapter")
        if i + 1 >= len(argv) or not argv[i + 1].isdigit():
            raise SystemExit("usage: python scripts/check.py [--solutions] --chapter N")
        targets = chapter_targets(int(argv[i + 1]))
        argv = argv[:i] + argv[i + 2:]
    else:
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
        print("node not found: skipping TypeScript exercises (needs Node >= 22.18; Node 24 LTS recommended)")
    if solutions:
        rc |= subprocess.call([sys.executable, str(ROOT / "scripts" / "spec_lint.py")], cwd=ROOT)
        rc |= subprocess.call([sys.executable, str(ROOT / "scripts" / "hints_lint.py")], cwd=ROOT)
        rc |= subprocess.call([sys.executable, str(ROOT / "scripts" / "contract_lint.py")], cwd=ROOT)
        rc |= subprocess.call([sys.executable, str(ROOT / "scripts" / "traceability.py"), "--check"], cwd=ROOT)
        rc |= subprocess.call([sys.executable, str(ROOT / "scripts" / "security_matrix.py")], cwd=ROOT)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
