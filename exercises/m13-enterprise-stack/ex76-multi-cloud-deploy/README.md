# ex76 · One service spec, three clouds (AWS, GCP, Azure)

**Module:** m13 Enterprise Stack · **Covers:** R06 Cloud platforms, R07 IaC, R25 Regulated data residency ·
**Hands-on:** AWS, GCP, Azure · **Time:** 60 min

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
