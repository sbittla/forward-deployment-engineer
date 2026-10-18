# ex76 · One service spec, three clouds (AWS, GCP, Azure)

**Module:** m13 Enterprise Stack · **Covers:** R06 Cloud platforms, R07 IaC, R25 Regulated data residency ·
**Hands-on:** AWS, GCP, Azure · **Time:** 60 min

## Learning objectives
- Translate one service spec into AWS, GCP and Azure deployment shapes.
- Compute the egress allowlist a security review will ask for.
- Handle data-residency requirements per cloud region.

## Scenario
Your company sells the same copilot to customers on all three clouds: a US bank on AWS, a German manufacturer on
Azure that requires EU data residency, and a retailer on GCP. FDEs constantly translate one architecture into each
customer's cloud vocabulary, and get asked in security review exactly which hostnames need egress. Write the
translator once.

## Your task
`ServiceSpec(name, image, cpu, memory_gb, min_instances, max_instances, region, env: dict, secrets: list[str])`.

1. `render(spec, cloud, account="")` returns a dict:
   | cloud | shape |
   |---|---|
   | `aws` (ECS Fargate task + service) | `{"family": name, "cpu": str(int(cpu*1024)), "memory": str(int(memory_gb*1024)), "containerDefinitions": [{"name", "image", "environment": [{"name","value"}…sorted by name], "secrets": [{"name": s, "valueFrom": f"arn:aws:secretsmanager:{region}:{account}:secret:{name}/{s}"}]}], "desiredCount": min_instances, "autoscaling": {"min": …, "max": …}}` |
   | `gcp` (Cloud Run) | `{"apiVersion": "serving.knative.dev/v1", "kind": "Service", "metadata": {"name", "annotations": {"autoscaling.knative.dev/minScale": str(min), "autoscaling.knative.dev/maxScale": str(max), "run.googleapis.com/region": region}}, "spec": {"template": {"spec": {"containers": [{"image", "resources": {"limits": {"cpu": str(cpu), "memory": f"{memory_gb}Gi"}}, "env": [... plain envs sorted, then {"name": s, "valueFrom": {"secretKeyRef": {"name": f"{name}-{s.lower()}", "key": "latest"}}}]}]}}}}` |
   | `azure` (Container Apps) | `{"type": "Microsoft.App/containerApps", "name", "location": region, "properties": {"configuration": {"secrets": [{"name": s.lower().replace("_","-"), "keyVaultUrl": f"https://{name}-kv.vault.azure.net/secrets/{s.lower().replace('_','-')}"}]}, "template": {"containers": [{"name", "image", "resources": {"cpu": cpu, "memory": f"{memory_gb}Gi"}, "env": [plain envs sorted, then {"name": s, "secretRef": s.lower().replace("_","-")}]}], "scale": {"minReplicas": min, "maxReplicas": max}}}}` |
   Unknown cloud → `ValueError`. Numbers like `0.5` CPU render as `"0.5"` (GCP) and `512` (AWS).
2. `model_endpoint(cloud, region, resource="")`: `aws` → `bedrock-runtime.{region}.amazonaws.com`;
   `gcp` → `{region}-aiplatform.googleapis.com`; `azure` → `{resource}.services.ai.azure.com`.
3. `egress_allowlist(spec, cloud, registry_host, resource="")` → sorted unique hostnames: the model endpoint, the
   registry host, and the cloud's secret service (`secretsmanager.{region}.amazonaws.com`,
   `secretmanager.googleapis.com`, `{name}-kv.vault.azure.net`).
4. `residency_violations(spec, cloud, jurisdiction)` → list of messages when `jurisdiction == "eu"` and the region is
   not an EU region for that cloud (`aws`: starts with `eu-`; `gcp`: starts with `europe-`; `azure`: one of
   `EU_AZURE_REGIONS`). Any other jurisdiction → `[]`.

## Prompt kit
**Learn (tutor prompt)**
```text
I'm preparing for a Forward Deployed Engineer role and working on the exercise "One service spec, three clouds (AWS,
GCP, Azure)". Before I write code, teach me the equivalent managed container services on AWS (ECS Fargate), GCP
(Cloud Run) and Azure (Container Apps), model endpoints on each cloud, and secret services. Use short Python
examples that are not the exercise solution. Then ask me three questions to check my understanding, one at a time,
and tell me what to re-read if I get one wrong.
```
**Build (coding-agent spec)**
```text
Implement exercises/m13-enterprise-stack/ex76-multi-cloud-deploy/starter.py so that test_multicloud.py passes.
README.md in that folder is the spec: follow its names, formats, ordering and error messages exactly. Public API:
`ServiceSpec`, `render`, `model_endpoint`, `egress_allowlist`, `residency_violations`. Constraints: Python 3.11+,
the standard library and the repo's fde_kit package only (pyyaml is allowed where the README uses YAML). Do not
modify the tests or fde_kit. When you're done, run `pytest exercises/m13-enterprise-stack/ex76-multi-cloud-deploy`
and show me the output. If the README and the tests disagree, stop and tell me instead of guessing.
```
**Review**
```text
Review my solution to "One service spec, three clouds (AWS, GCP, Azure)" as a senior forward deployed engineer would
before it ships to a customer. Specifically: Are CPU and memory units correct for each cloud? Is the allowlist
complete for a locked-down network? Which cloud-specific settings would a platform team still require? Rank findings
by customer impact, quote the line for each, and say which ones a test should catch.
```
