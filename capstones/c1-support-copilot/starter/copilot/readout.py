"""Executive readout generated from measured metrics, so the slide numbers can't drift from reality."""
from .evals import launch_bar


def business_impact(baseline_aht_min: float, projected_aht_min: float, monthly_contacts: int,
                    hourly_cost: float, adoption: float, monthly_llm_cost: float) -> dict:
    raise NotImplementedError


def render_exec_readout(metrics: dict, impact: dict, customer: str = "Northwind Insurance") -> str:
    raise NotImplementedError
