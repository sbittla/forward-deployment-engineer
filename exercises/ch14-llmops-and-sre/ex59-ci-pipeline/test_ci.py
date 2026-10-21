import copy

import yaml

GOOD = yaml.safe_load("""
name: ci
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
  id-token: write
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b
        with: {python-version: "${{ matrix.python-version }}"}
      - run: pip install -r requirements.txt && pytest --solutions
  deploy:
    needs: [test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh
        env: {TOKEN: "${{ secrets.DEPLOY_TOKEN }}"}
""")


def test_good(impl):
    assert impl.lint_workflow(GOOD) == []


def test_bad(impl):
    d = copy.deepcopy(GOOD)
    d[True] = {"push": None}
    d["permissions"] = "write-all"
    del d["jobs"]["test"]["timeout-minutes"]
    d["jobs"]["test"]["steps"][0]["uses"] = "actions/checkout@main"
    d["jobs"]["test"]["steps"].append({"run": 'echo "token=${{ secrets.DEPLOY_TOKEN }}"'})
    d["jobs"]["test"]["strategy"]["matrix"]["python-version"] = ["3.12"]
    d["jobs"]["deploy"]["needs"] = []
    assert set(impl.lint_workflow(d)) == {"triggers", "permissions", "timeout:test", "pin:test",
                                          "secret-echo:test", "matrix", "deploy-gate"}


def test_write_scope_and_unpinned(impl):
    d = copy.deepcopy(GOOD)
    d["permissions"] = {"contents": "write"}
    d["jobs"]["deploy"]["steps"][0]["uses"] = "someorg/action"
    del d["jobs"]["deploy"]["if"]
    assert set(impl.lint_workflow(d)) == {"permissions", "pin:deploy", "deploy-gate"}


def test_long_lived_cloud_key_flagged(impl):
    d = copy.deepcopy(GOOD)
    d["jobs"]["deploy"]["steps"][1]["env"] = {"AWS_SECRET_ACCESS_KEY": "${{ secrets.AWS_SECRET_ACCESS_KEY }}"}
    assert impl.lint_workflow(d) == ["static-cloud-key:deploy"]
    d = copy.deepcopy(GOOD)
    d["jobs"]["deploy"]["env"] = {"GOOGLE_CREDENTIALS": "${{ secrets.GOOGLE_CREDENTIALS }}"}
    assert impl.lint_workflow(d) == ["static-cloud-key:deploy"]


def test_your_workflow(impl, exercise_dir):
    doc = yaml.safe_load((exercise_dir / "ci.yml").read_text())
    assert impl.lint_workflow(doc) == []
    assert set(doc["jobs"]) >= {"test", "deploy"}
    runs = " ".join(s.get("run", "") for s in doc["jobs"]["test"]["steps"])
    assert "pytest" in runs
