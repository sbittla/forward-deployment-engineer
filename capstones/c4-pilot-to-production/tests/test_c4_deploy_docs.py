import re

import pytest
import yaml

PACKAGE = "pilot"


def test_policy_catches_the_legacy_setup(cap):
    assert set(cap.lint_dockerfile("FROM python\nCOPY . .\nENV API_KEY=abc\nCMD python app.py")) == {
        "pinned-base", "non-root", "healthcheck", "exec-form", "no-secrets"}
    bad = [{"kind": "Deployment", "metadata": {"name": "s"}, "spec": {"replicas": 1, "template": {"spec": {
        "containers": [{"name": "c", "image": "s:latest", "env": [{"name": "API_KEY", "value": "x"}]}]}}}}]
    assert set(cap.lint_k8s(bad)) == {"s: replicas", "s: non-root", "s: resources", "s: livenessProbe",
                                      "s: readinessProbe", "s: image-tag", "s: secret-literal"}
    assert set(cap.lint_ci({"jobs": {"b": {"steps": [{"uses": "actions/checkout@main"}, {"run": "make"}]}}})) == {
        "permissions", "timeout:b", "pin:b", "tests"}


def test_your_deploy_artifacts_pass(cap, cap_dir):
    d = cap_dir / "deploy"
    assert cap.lint_dockerfile((d / "Dockerfile").read_text()) == []
    docs = [x for x in yaml.safe_load_all((d / "k8s.yaml").read_text()) if x]
    assert cap.lint_k8s(docs) == []
    assert any(x["kind"] == "HorizontalPodAutoscaler" for x in docs)
    assert cap.lint_ci(yaml.safe_load((d / "ci.yml").read_text())) == []


REQUIRED = {
    "production_readiness_review.md": ["Summary", "Assumptions", "Incident findings", "Checklist", "Capacity",
                                       "Open risks", "Sign-off"],
    "runbook.md": ["Overview", "Deploy", "Rollback", "Alerts", "Degraded mode", "Customer environment", "Escalation"],
}


@pytest.mark.parametrize("name", sorted(REQUIRED))
def test_deliverables(cap_dir, name):
    text = (cap_dir / "deliverables" / name).read_text(encoding="utf-8")
    headings = [h.lower() for h in re.findall(r"^#+\s+(.*)$", text, re.M)]
    for section in REQUIRED[name]:
        assert any(section.lower() in h for h in headings), f"{name}: missing '{section}'"
    assert not re.search(r"TODO|TBD|FIXME", text)
    if name == "production_readiness_review.md":
        assert text.count("[x]") >= 8, "checklist needs at least 8 completed items"
