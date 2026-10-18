"""Spec lint: every public name a test uses must be documented in the exercise README.

Learners implement from the README, so a test that calls an undocumented function is a spec bug.
usage: python scripts/spec_lint.py
"""
import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TS_IMPORT = re.compile(r"import\s*\{([^}]*)\}\s*from\s*[\"'][^\"']*(?:starter|solution|target)[^\"']*[\"']", re.S)
TS_DYNAMIC = re.compile(r"\b(?:m|mod|impl)\.([A-Za-z_]\w*)")
TS_CONST = re.compile(r"^export\s+const\s+(\w+)\s*(?::[^=]+)?=\s*(?!\(|async|function)", re.M)


def python_names(test: pathlib.Path) -> set[str]:
    names = set()
    for node in ast.walk(ast.parse(test.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id in ("impl", "cap"):
            names.add(node.attr)
    return {n for n in names if not n.startswith("_")}


def ts_names(test: pathlib.Path) -> set[str]:
    text = test.read_text(encoding="utf-8")
    names = set()
    for group in TS_IMPORT.findall(text):
        names |= {part.split(" as ")[0].strip().removeprefix("type ").strip() for part in group.split(",") if part.strip()}
    names |= set(TS_DYNAMIC.findall(text))
    return {n for n in names if n}


def _is_stub(fn) -> bool:
    body = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
    return len(body) == 1 and isinstance(body[0], ast.Raise)


def provided(d: pathlib.Path) -> set[str]:
    """Names the starter already gives the learner (constants, data classes, working functions)."""
    names = set()
    for starter in d.glob("starter.py"):
        for node in ast.parse(starter.read_text(encoding="utf-8")).body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                names |= {t.id for t in targets if isinstance(t, ast.Name)}
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not _is_stub(node):
                names.add(node.name)
            elif isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                if not any(_is_stub(m) for m in methods):
                    names.add(node.name)
    for starter in d.glob("starter.ts"):
        names |= set(TS_CONST.findall(starter.read_text(encoding="utf-8")))
    return names


def check_dir(d: pathlib.Path, docs: str) -> list[str]:
    problems = []
    given = provided(d)
    for test in sorted(d.rglob("test_*.py")) + sorted(d.rglob("*.test.ts")):
        names = python_names(test) if test.suffix == ".py" else ts_names(test)
        for name in sorted(names):
            if name not in given and not re.search(rf"\b{re.escape(name)}\b", docs):
                problems.append(f"{test.relative_to(ROOT).as_posix()}: `{name}` is used by tests but not in the README")
    return problems


def main() -> int:
    problems = []
    for readme in sorted(ROOT.glob("exercises/*/*/README.md")):
        spec = readme.read_text(encoding="utf-8").split("## Prompt kit")[0]   # the kit lists names; it isn't the spec
        problems += check_dir(readme.parent, spec)
    for cap in sorted(ROOT.glob("capstones/*/")):
        docs = "\n".join(p.read_text(encoding="utf-8") for p in cap.rglob("*.md"))
        docs += "\n".join(p.read_text(encoding="utf-8") for p in (cap / "starter").rglob("*.py"))
        docs += "\n".join(p.read_text(encoding="utf-8") for p in (cap / "starter").rglob("*.ts"))
        problems += check_dir(cap / "tests", docs)
    for p in problems:
        print(p)
    print(f"spec-lint: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
