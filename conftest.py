"""Test harness shared by every exercise and capstone.

Each exercise's tests request the `impl` fixture. By default it loads the
learner's `starter.py` next to the test file. With `--solutions` it loads the
reference `solution.py` from the mirrored path under `solutions/`.

Capstones ship a package directory (`starter/` or the mirrored solution dir);
the `cap` fixture puts the right one on sys.path and imports the package.
"""
import importlib
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


def pytest_addoption(parser):
    parser.addoption("--solutions", action="store_true", help="test reference solutions instead of starters")


def _target_dir(request, kind: str) -> Path:
    test_dir = Path(str(request.fspath)).parent
    if not request.config.getoption("--solutions"):
        return test_dir
    rel = test_dir.relative_to(ROOT / kind)
    return ROOT / "solutions" / kind / rel


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def impl(request):
    d = _target_dir(request, "exercises")
    fname = "solution.py" if request.config.getoption("--solutions") else "starter.py"
    return load_module(d / fname, f"fde_{d.parent.name}_{d.name}".replace("-", "_"))


@pytest.fixture
def exercise_dir(request):
    """Directory holding the code under test (starter or solution)."""
    return _target_dir(request, "exercises")


@pytest.fixture
def cap(request):
    """Import the capstone package (name given by the test module's PACKAGE)."""
    test_dir = Path(str(request.fspath)).parent
    cap_root = test_dir.parent  # capstones/cN-name/
    if request.config.getoption("--solutions"):
        base = ROOT / "solutions" / "capstones" / cap_root.name
    else:
        base = cap_root / "starter"
    pkg = request.module.PACKAGE
    for m in [m for m in sys.modules if m == pkg or m.startswith(pkg + ".")]:
        del sys.modules[m]
    sys.path.insert(0, str(base))
    try:
        yield importlib.import_module(pkg)
    finally:
        sys.path.remove(str(base))
