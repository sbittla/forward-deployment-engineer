"""Check every exercise and capstone has a HINTS.md that helps without handing over the solution.

Rules: three progressive hints in <details> blocks, a "When a test fails" table, every test it names exists in the
exercise's tests, and no fenced code block longer than MAX_CODE_LINES (hints point the way; they don't write it).
usage: python scripts/hints_lint.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_CODE_LINES = 4
TEST_DEF = re.compile(r"""^\s*(?:async\s+)?def\s+(test_\w+)|^\s*test\(\s*["'`]([^"'`]+)["'`]""", re.M)


def exercise_dirs() -> list[Path]:
    dirs = sorted(p.parent for p in (ROOT / "exercises").glob("*/*/README.md"))
    return dirs + sorted(p.parent for p in (ROOT / "capstones").glob("*/README.md"))


def test_names(ex: Path) -> set[str]:
    names: set[str] = set()
    for p in ex.rglob("*"):
        if p.is_file() and (p.name.startswith("test_") and p.suffix == ".py" or p.name.endswith(".test.ts")):
            for m in TEST_DEF.finditer(p.read_text(encoding="utf-8")):
                names.add(m.group(1) or m.group(2))
    return names


def check(ex: Path) -> list[str]:
    hints = ex / "HINTS.md"
    if not hints.exists():
        return ["missing HINTS.md"]
    text = hints.read_text(encoding="utf-8")
    problems = []
    if len(re.findall(r"<summary>Hint \d", text)) != 3:
        problems.append("needs exactly three '<summary>Hint N' blocks")
    if "## When a test fails" not in text:
        problems.append("missing '## When a test fails' section")
    known = test_names(ex)
    table = text.split("## When a test fails", 1)[-1]
    for name in re.findall(r"^\|\s*`([^`]+)`", table, re.M):
        if name not in known:
            problems.append(f"names a test that doesn't exist: {name}")
    for block in re.findall(r"^```[^\n]*\n(.*?)^```", text, re.M | re.S):
        if block.count("\n") > MAX_CODE_LINES:
            problems.append(f"code block longer than {MAX_CODE_LINES} lines")
    return problems


def main() -> int:
    bad = 0
    for ex in exercise_dirs():
        for problem in check(ex):
            print(f"{ex.relative_to(ROOT).as_posix()}: {problem}")
            bad += 1
    print(f"hints-lint: {bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
