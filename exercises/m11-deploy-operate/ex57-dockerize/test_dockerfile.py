import pytest

BAD = """FROM python
ENV API_KEY=sk-live-please-dont
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD python -m app
"""

GOOD = """FROM python:3.12-slim AS base
ARG BUILD_TOKEN=
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir \\
      -r requirements.txt
COPY . .
RUN useradd --uid 10001 app
USER 10001
HEALTHCHECK CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')"]
EXPOSE 8080
CMD ["python", "-m", "app"]
"""


def test_bad_has_all_issues(impl):
    assert set(impl.lint_dockerfile(BAD)) == {"pinned-base", "non-root", "healthcheck", "no-secrets",
                                               "layer-cache", "no-cache-dir", "exec-form"}


def test_good_clean(impl):
    assert impl.lint_dockerfile(GOOD) == []


@pytest.mark.parametrize("snippet,rule", [
    ("FROM python:latest", "pinned-base"),
    ("FROM python@sha256:abc123", None),
    ("USER root", "non-root"),
    ('CMD ["x"]\nUSER app', "non-root"),
    ("env DB_PASSWORD=hunter2", "no-secrets"),
    ("ARG GITHUB_TOKEN", None),
])
def test_rules(impl, snippet, rule):
    base = GOOD.replace("FROM python:3.12-slim AS base", "FROM python:3.12-slim")
    text = base + "\n" + snippet if not snippet.startswith("FROM") else base.replace("FROM python:3.12-slim", snippet)
    issues = impl.lint_dockerfile(text)
    if rule:
        assert rule in issues
    else:
        assert issues == []


def test_your_dockerfile_passes(impl, exercise_dir):
    text = (exercise_dir / "Dockerfile").read_text()
    assert impl.lint_dockerfile(text) == []
    assert "8080" in text and "app" in text
