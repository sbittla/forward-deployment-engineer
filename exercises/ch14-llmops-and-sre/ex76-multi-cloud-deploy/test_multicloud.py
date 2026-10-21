import pytest


@pytest.fixture
def spec(impl):
    return impl.ServiceSpec(name="copilot", image="reg.example/copilot:1.2.0", cpu=0.5, memory_gb=1, min_instances=2,
                            max_instances=8, region="eu-central-1", env={"LOG_LEVEL": "INFO", "APP_ENV": "prod"},
                            secrets=["MODEL_API_KEY"])


def test_aws(impl, spec):
    out = impl.render(spec, "aws", account="111122223333")
    assert out["family"] == "copilot" and out["cpu"] == "512" and out["memory"] == "1024"
    c = out["containerDefinitions"][0]
    assert c["environment"] == [{"name": "APP_ENV", "value": "prod"}, {"name": "LOG_LEVEL", "value": "INFO"}]
    assert c["secrets"] == [{"name": "MODEL_API_KEY",
                             "valueFrom": "arn:aws:secretsmanager:eu-central-1:111122223333:secret:copilot/MODEL_API_KEY"}]
    assert out["desiredCount"] == 2 and out["autoscaling"] == {"min": 2, "max": 8}


def test_gcp(impl, spec):
    spec.region = "europe-west4"
    out = impl.render(spec, "gcp")
    assert out["kind"] == "Service" and out["apiVersion"] == "serving.knative.dev/v1"
    ann = out["metadata"]["annotations"]
    assert ann["autoscaling.knative.dev/minScale"] == "2" and ann["autoscaling.knative.dev/maxScale"] == "8"
    assert ann["run.googleapis.com/region"] == "europe-west4"
    c = out["spec"]["template"]["spec"]["containers"][0]
    assert c["resources"]["limits"] == {"cpu": "0.5", "memory": "1Gi"}
    assert c["env"][0] == {"name": "APP_ENV", "value": "prod"}
    assert c["env"][-1] == {"name": "MODEL_API_KEY", "valueFrom": {"secretKeyRef": {"name": "copilot-model_api_key", "key": "latest"}}}


def test_azure(impl, spec):
    spec.region = "germanywestcentral"
    out = impl.render(spec, "azure")
    assert out["type"] == "Microsoft.App/containerApps" and out["location"] == "germanywestcentral"
    sec = out["properties"]["configuration"]["secrets"][0]
    assert sec == {"name": "model-api-key", "keyVaultUrl": "https://copilot-kv.vault.azure.net/secrets/model-api-key"}
    tpl = out["properties"]["template"]
    assert tpl["scale"] == {"minReplicas": 2, "maxReplicas": 8}
    c = tpl["containers"][0]
    assert c["resources"] == {"cpu": 0.5, "memory": "1Gi"} and c["env"][-1] == {"name": "MODEL_API_KEY", "secretRef": "model-api-key"}


def test_unknown_cloud(impl, spec):
    with pytest.raises(ValueError):
        impl.render(spec, "oracle")


def test_endpoints_and_egress(impl, spec):
    assert impl.model_endpoint("aws", "us-east-1") == "bedrock-runtime.us-east-1.amazonaws.com"
    assert impl.model_endpoint("gcp", "europe-west4") == "europe-west4-aiplatform.googleapis.com"
    assert impl.model_endpoint("azure", "westeurope", resource="contoso-ai") == "contoso-ai.services.ai.azure.com"
    assert impl.egress_allowlist(spec, "aws", "reg.example") == [
        "bedrock-runtime.eu-central-1.amazonaws.com", "reg.example", "secretsmanager.eu-central-1.amazonaws.com"]
    spec.region = "westeurope"
    assert impl.egress_allowlist(spec, "azure", "reg.example", resource="contoso-ai") == [
        "contoso-ai.services.ai.azure.com", "copilot-kv.vault.azure.net", "reg.example"]


def test_residency(impl, spec):
    assert impl.residency_violations(spec, "aws", "eu") == []
    spec.region = "us-east-1"
    v = impl.residency_violations(spec, "aws", "eu")
    assert len(v) == 1 and "us-east-1" in v[0]
    spec.region = "eastus"
    assert impl.residency_violations(spec, "azure", "eu") and impl.residency_violations(spec, "azure", "us") == []
    spec.region = "europe-west1"
    assert impl.residency_violations(spec, "gcp", "eu") == []
