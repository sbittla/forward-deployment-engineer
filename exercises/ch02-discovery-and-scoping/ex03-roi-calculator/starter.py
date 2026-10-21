def annual_labor_savings(tasks_per_month, minutes_saved, hourly_cost, adoption=1.0):
    raise NotImplementedError


def annual_llm_cost(tasks_per_month, in_tokens, out_tokens, price_in_mtok, price_out_mtok, calls_per_task=1):
    raise NotImplementedError


def payback_months(one_time_cost, monthly_net_benefit):
    raise NotImplementedError


def roi_summary(**inputs) -> dict:
    raise NotImplementedError


def sensitivity(inputs: dict, param, multipliers) -> list[tuple[float, float]]:
    raise NotImplementedError


def full_case(review_rate, review_minutes, annual_ops_cost, **inputs) -> dict:
    raise NotImplementedError
