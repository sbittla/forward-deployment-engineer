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


def render(spec: ServiceSpec, cloud: str, account: str = "") -> dict:
    raise NotImplementedError


def model_endpoint(cloud: str, region: str, resource: str = "") -> str:
    raise NotImplementedError


def egress_allowlist(spec: ServiceSpec, cloud: str, registry_host: str, resource: str = "") -> list[str]:
    raise NotImplementedError


def residency_violations(spec: ServiceSpec, cloud: str, jurisdiction: str) -> list[str]:
    raise NotImplementedError
