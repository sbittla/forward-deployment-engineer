from dataclasses import dataclass, field

EU_AZURE_REGIONS = {"westeurope", "northeurope", "germanywestcentral", "francecentral", "swedencentral",
                    "italynorth", "polandcentral", "spaincentral"}


@dataclass
class ServiceSpec:
    name: str
    image: str
    cpu: float
    memory_gb: float
    min_instances: int
    max_instances: int
    region: str
    env: dict = field(default_factory=dict)
    secrets: list = field(default_factory=list)


def _num(x) -> str:
    return str(int(x)) if float(x).is_integer() else str(x)


def _plain_env(spec):
    return [{"name": k, "value": v} for k, v in sorted(spec.env.items())]


def _kebab(s: str) -> str:
    return s.lower().replace("_", "-")


def _aws(spec, account):
    return {
        "family": spec.name,
        "cpu": str(int(spec.cpu * 1024)),
        "memory": str(int(spec.memory_gb * 1024)),
        "containerDefinitions": [{
            "name": spec.name,
            "image": spec.image,
            "environment": _plain_env(spec),
            "secrets": [{"name": s, "valueFrom": f"arn:aws:secretsmanager:{spec.region}:{account}:secret:{spec.name}/{s}"}
                        for s in spec.secrets],
        }],
        "desiredCount": spec.min_instances,
        "autoscaling": {"min": spec.min_instances, "max": spec.max_instances},
    }


def _gcp(spec):
    env = _plain_env(spec) + [
        {"name": s, "valueFrom": {"secretKeyRef": {"name": f"{spec.name}-{s.lower()}", "key": "latest"}}}
        for s in spec.secrets]
    return {
        "apiVersion": "serving.knative.dev/v1",
        "kind": "Service",
        "metadata": {"name": spec.name, "annotations": {
            "autoscaling.knative.dev/minScale": str(spec.min_instances),
            "autoscaling.knative.dev/maxScale": str(spec.max_instances),
            "run.googleapis.com/region": spec.region}},
        "spec": {"template": {"spec": {"containers": [{
            "image": spec.image,
            "resources": {"limits": {"cpu": _num(spec.cpu), "memory": f"{_num(spec.memory_gb)}Gi"}},
            "env": env}]}}},
    }


def _azure(spec):
    return {
        "type": "Microsoft.App/containerApps",
        "name": spec.name,
        "location": spec.region,
        "properties": {
            "configuration": {"secrets": [
                {"name": _kebab(s), "keyVaultUrl": f"https://{spec.name}-kv.vault.azure.net/secrets/{_kebab(s)}"}
                for s in spec.secrets]},
            "template": {
                "containers": [{"name": spec.name, "image": spec.image,
                                "resources": {"cpu": spec.cpu, "memory": f"{_num(spec.memory_gb)}Gi"},
                                "env": _plain_env(spec) + [{"name": s, "secretRef": _kebab(s)} for s in spec.secrets]}],
                "scale": {"minReplicas": spec.min_instances, "maxReplicas": spec.max_instances},
            },
        },
    }


def render(spec: ServiceSpec, cloud: str, account: str = "") -> dict:
    if cloud == "aws":
        return _aws(spec, account)
    if cloud == "gcp":
        return _gcp(spec)
    if cloud == "azure":
        return _azure(spec)
    raise ValueError(f"unsupported cloud {cloud!r}")


def model_endpoint(cloud: str, region: str, resource: str = "") -> str:
    return {
        "aws": f"bedrock-runtime.{region}.amazonaws.com",
        "gcp": f"{region}-aiplatform.googleapis.com",
        "azure": f"{resource}.services.ai.azure.com",
    }[cloud]


def egress_allowlist(spec: ServiceSpec, cloud: str, registry_host: str, resource: str = "") -> list[str]:
    secrets_host = {
        "aws": f"secretsmanager.{spec.region}.amazonaws.com",
        "gcp": "secretmanager.googleapis.com",
        "azure": f"{spec.name}-kv.vault.azure.net",
    }[cloud]
    return sorted({model_endpoint(cloud, spec.region, resource), registry_host, secrets_host})


def residency_violations(spec: ServiceSpec, cloud: str, jurisdiction: str) -> list[str]:
    if jurisdiction != "eu":
        return []
    in_eu = {
        "aws": spec.region.startswith("eu-"),
        "gcp": spec.region.startswith("europe-"),
        "azure": spec.region in EU_AZURE_REGIONS,
    }[cloud]
    return [] if in_eu else [f"{cloud} region {spec.region} is outside the EU; customer requires EU data residency"]
