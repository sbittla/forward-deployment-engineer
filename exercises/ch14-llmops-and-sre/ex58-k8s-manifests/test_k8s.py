import copy

import yaml

GOOD = yaml.safe_load_all("""
apiVersion: apps/v1
kind: Deployment
metadata: {name: web}
spec:
  replicas: 3
  selector: {matchLabels: {app: web}}
  template:
    metadata: {labels: {app: web, tier: api}}
    spec:
      securityContext: {runAsNonRoot: true}
      containers:
        - name: app
          image: reg/web:1.4.2
          resources:
            requests: {cpu: 250m, memory: 256Mi}
            limits: {cpu: "1", memory: 512Mi}
          livenessProbe: {httpGet: {path: /healthz, port: 8080}}
          readinessProbe: {httpGet: {path: /healthz, port: 8080}}
          securityContext: {readOnlyRootFilesystem: true}
          env:
            - name: API_KEY
              valueFrom: {secretKeyRef: {name: web, key: api-key}}
            - name: LOG_LEVEL
              value: INFO
---
apiVersion: v1
kind: Service
metadata: {name: web}
spec: {selector: {app: web}, ports: [{port: 80, targetPort: 8080}]}
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: {name: web}
spec:
  scaleTargetRef: {apiVersion: apps/v1, kind: Deployment, name: web}
  minReplicas: 2
  maxReplicas: 10
""")
GOOD = [d for d in GOOD if d]


def test_good_is_clean(impl):
    assert impl.lint_manifests(GOOD) == []


def test_many_violations(impl):
    docs = copy.deepcopy(GOOD)
    dep, svc, hpa = docs
    dep["spec"]["replicas"] = 1
    pod = dep["spec"]["template"]["spec"]
    del pod["securityContext"]
    c = pod["containers"][0]
    c["image"] = "reg/web:latest"
    del c["resources"]["limits"]
    del c["readinessProbe"]
    c["securityContext"] = {}
    c["env"].append({"name": "DB_PASSWORD", "value": "hunter2"})
    svc["spec"]["selector"] = {"app": "wrong"}
    hpa["spec"]["minReplicas"] = 1
    hpa["spec"]["scaleTargetRef"]["name"] = "nope"
    issues = set(impl.lint_manifests(docs))
    assert issues == {
        "Deployment/web: replicas", "Deployment/web: resources:app", "Deployment/web: readiness:app",
        "Deployment/web: image-tag:app", "Deployment/web: secret-literal:app", "Deployment/web: non-root",
        "Deployment/web: readonly-fs:app", "Service/web: selector", "HorizontalPodAutoscaler/web: hpa-min",
        "HorizontalPodAutoscaler/web: hpa-target",
    }


def test_untagged_image(impl):
    docs = copy.deepcopy(GOOD)
    docs[0]["spec"]["template"]["spec"]["containers"][0]["image"] = "reg/web"
    assert "Deployment/web: image-tag:app" in impl.lint_manifests(docs)


def test_selector_subset_ok(impl):
    # Service selector is a subset of pod labels -> matches
    assert impl.lint_manifests(GOOD) == []


def test_your_manifests(impl, exercise_dir):
    docs = impl.load(exercise_dir / "deploy.yaml")
    kinds = sorted(d["kind"] for d in docs)
    assert kinds == ["Deployment", "HorizontalPodAutoscaler", "Service"]
    assert impl.lint_manifests(docs) == []
    dep = next(d for d in docs if d["kind"] == "Deployment")
    assert dep["metadata"]["name"] == "answer-svc"
    env = dep["spec"]["template"]["spec"]["containers"][0].get("env", [])
    assert any("secretKeyRef" in e.get("valueFrom", {}) for e in env)
