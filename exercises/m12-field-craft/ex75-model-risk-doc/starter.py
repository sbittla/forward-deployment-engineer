REQUIRED = ("name", "version", "owner", "purpose", "users", "out_of_scope", "data_sources", "model_provider",
            "evals", "limitations", "monitoring", "human_oversight")
FLAGS = ("customer_facing", "automated_decision", "regulated_domain")


def risk_tier(meta: dict) -> int:
    raise NotImplementedError


def required_controls(tier: int) -> list[str]:
    raise NotImplementedError


def validate(meta: dict) -> list[str]:
    raise NotImplementedError


def render(meta: dict) -> str:
    raise NotImplementedError
