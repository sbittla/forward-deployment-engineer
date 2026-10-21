GOOD = """# Answer service runbook

## Overview
Serves copilot answers. Owned by Claims Platform.

## Prerequisites
Set NAMESPACE to the target namespace and IMAGE_TAG to the release tag.

## Deploy
```bash
kubectl -n <NAMESPACE> set image deploy/answer-svc app=reg/answer-svc:<IMAGE_TAG>
```

## Rollback
```bash
kubectl -n <NAMESPACE> rollout undo deploy/answer-svc
```

## Monitoring
Dashboard: Grafana > Copilot > Answer SLO.

## Escalation
On-call: claims-platform-oncall@northwind.example, +1 415 555 0100.
"""

BAD = """# Runbook

### Deploy
```
kubectl apply -f <MANIFEST>
```

## Rollback
TODO: write this

## Escalation
Ask in Slack.
"""


def test_good(impl):
    assert impl.lint_runbook(GOOD) == []


def test_bad(impl):
    assert impl.lint_runbook(BAD) == [
        "L3: heading-skip",
        "L4: code-lang",
        "L9: placeholder",
        "missing-section:Overview",
        "missing-section:Prerequisites",
        "missing-section:Monitoring",
        "rollback-command",
        "escalation-contact",
        "undocumented-variable:MANIFEST",
    ]


def test_heading_with_extra_words(impl):
    doc = GOOD.replace("## Rollback", "## Rollback procedure")
    assert impl.lint_runbook(doc) == []


def test_fence_in_wrong_section_doesnt_count(impl):
    doc = GOOD.replace("## Rollback\n```bash\nkubectl -n <NAMESPACE> rollout undo deploy/answer-svc\n```",
                       "## Rollback\nUndo the rollout.")
    assert impl.lint_runbook(doc) == ["rollback-command"]


def test_your_runbook(impl, exercise_dir):
    text = (exercise_dir / "RUNBOOK.md").read_text(encoding="utf-8")
    assert impl.lint_runbook(text) == []
    assert "answer" in text.lower()
