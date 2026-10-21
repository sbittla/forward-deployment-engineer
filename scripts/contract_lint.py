"""Check that every exercise and capstone README carries the reproducibility contract, a "## Run and verify" section.

The contract answers, for each suite: prerequisites, the command to run your work, the expected output, how to check
the reference solution, which tests run, common failures, how to tell whose failure it is, cleanup, and production
caveats. `--write` (re)generates the mechanical lines from the latest full report in output/ and keeps each README's
own production caveats; run `python scripts/run_all.py --docker` first so the counts are current.

usage: python scripts/contract_lint.py [--write]
"""
import json
import textwrap
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADING = "## Run and verify"
FIELDS = ["Prerequisites", "Run your work", "Expected output", "Check the reference solution", "Tests",
          "Common failures", "Whose failure is it?", "Cleanup", "Production caveats"]
PLACEHOLDER = "<!-- caveats -->"
WIDTH = 117
SECTION = re.compile(rf"^{re.escape(HEADING)}\n.*?(?=^## |\Z)", re.M | re.S)


def suites() -> list[Path]:
    exercises = sorted(p.parent for p in (ROOT / "exercises").glob("*/*/README.md"))
    return exercises + sorted(p.parent for p in (ROOT / "capstones").glob("c*/README.md"))


def test_files(d: Path) -> tuple[list[Path], list[Path]]:
    py = sorted(p for p in d.rglob("test_*.py") if "__pycache__" not in p.parts)
    ts = [] if d.parent.name == "capstones" else sorted(d.glob("*.test.ts"))
    return py, ts


def caveats(text: str) -> str:
    m = re.search(r"^- \*\*Production caveats:\*\* (.+?)(?=^\S|\Z)", text, re.M | re.S)
    return " ".join(m.group(1).split()) if m else PLACEHOLDER


def render(d: Path, result: dict, keep: str) -> str:
    rel = d.relative_to(ROOT).as_posix()
    py, ts = test_files(d)
    ran, failing = result["ran"], result["starter_failing"]
    node = ts and "; Node.js 22.18 or later (24 LTS recommended) for the TypeScript tests, with no `npm install`" or ""
    runs, refs = [], []
    if py:
        runs.append(f"`pytest {rel}`")
        refs.append(f"`pytest --solutions {rel}`")
    for t in ts:
        t = t.relative_to(ROOT).as_posix()
        runs.append(f"`node --test {t}`")
        refs.append(f"`FDE_SOLUTIONS=1 node --test {t}` (PowerShell: `$env:FDE_SOLUTIONS=1; node --test {t}`)")
    files = ", ".join(f"`{p.relative_to(d).as_posix()}`" for p in py + ts)
    starter = (f"all {ran} tests fail against the starter" if failing == ran else
               f"{failing} of the {ran} tests fail against the starter ("
               + ("the one that passes checks" if ran - failing == 1 else f"the {ran - failing} that pass check")
               + " scaffolding the starter already provides)")
    lines = [
        f"- **Prerequisites:** Python 3.11 or later and `pip install -r requirements.txt`, run once from the repository "
        f"root{node}. No API key or network access is needed.",
        f"- **Run your work:** from the repository root, {' and '.join(runs)}.",
        f"- **Expected output:** {starter}; when you're done, all {ran} pass.",
        f"- **Check the reference solution:** {' and '.join(refs)}: all {ran} pass.",
        f"- **Tests:** {files} ({ran} tests).",
        "- **Common failures:** `ModuleNotFoundError: No module named 'fde_kit'` means the command didn't run from the "
        "repository root" + ("; a Node.js error about the `.ts` extension means Node is older than 22.18" if ts else "")
        + ". For a failing test, [HINTS.md](HINTS.md) says what it usually means.",
        "- **Whose failure is it?** If your run fails but the reference run passes, it's your code. If the reference "
        "run fails too, check the prerequisites (`python --version`, `node --version`); if they're met, it's a defect in "
        "the published solution, so report it with the repository's Errata issue template.",
        "- **Cleanup:** none. The tests write only to temporary directories, and `__pycache__` folders are ignored by "
        "git.",
        f"- **Production caveats:** {keep}"]
    wrapped = [wrap(line) for line in lines]
    return "\n".join([HEADING, ""] + wrapped + ["", ""])


def wrap(line: str) -> str:
    """Wrap a list item without breaking inside `inline code`, so commands stay copyable."""
    keep = re.sub(r"`[^`]+`", lambda m: m.group(0).replace(" ", "\x00"), line)
    out = textwrap.fill(keep, WIDTH, subsequent_indent="  ", break_long_words=False, break_on_hyphens=False)
    return out.replace("\x00", " ")


def main(write: bool) -> int:
    problems = 0
    for d in suites():
        readme = d / "README.md"
        text = readme.read_bytes().decode("utf-8")
        nl = "\r\n" if "\r\n" in text else "\n"
        text = text.replace("\r\n", "\n")
        rel = d.relative_to(ROOT).as_posix()
        if write:
            result = json.loads((ROOT / "output" / rel / "result.json").read_text(encoding="utf-8"))
            section = render(d, result, caveats(text))
            if SECTION.search(text):
                text = SECTION.sub(lambda _: section, text, count=1)
            elif "## Prompt kit" in text:
                text = text.replace("## Prompt kit", section + "## Prompt kit", 1)
            else:
                text = text.rstrip("\n") + "\n\n" + section.rstrip("\n") + "\n"
            readme.write_bytes(text.replace("\n", nl).encode("utf-8"))
        m = SECTION.search(text)
        errs = []
        if not m:
            errs.append(f"missing '{HEADING}'")
        else:
            body = m.group(0)
            errs += [f"missing field '{f}'" for f in FIELDS if f"- **{f}" not in body]
            if PLACEHOLDER in body:
                errs.append("production caveats not written yet")
            if rel not in body:
                errs.append("run command doesn't name this folder")
            py, ts = test_files(d)
            errs += [f"tests field omits {p.name}" for p in py + ts if p.relative_to(d).as_posix() not in body]
        for e in errs:
            print(f"{rel}: {e}")
        problems += len(errs)
    print(f"contract-lint: {problems} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
