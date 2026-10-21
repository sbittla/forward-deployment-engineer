import math


def annual_labor_savings(tasks_per_month, minutes_saved, hourly_cost, adoption=1.0):
    return tasks_per_month * 12 * adoption * minutes_saved / 60 * hourly_cost


def annual_llm_cost(tasks_per_month, in_tokens, out_tokens, price_in_mtok, price_out_mtok, calls_per_task=1):
    per_call = in_tokens * price_in_mtok / 1e6 + out_tokens * price_out_mtok / 1e6
    return per_call * calls_per_task * tasks_per_month * 12


def payback_months(one_time_cost, monthly_net_benefit):
    if monthly_net_benefit <= 0:
        return math.inf
    return one_time_cost / monthly_net_benefit


def roi_summary(**i) -> dict:
    savings = annual_labor_savings(i["tasks_per_month"], i["minutes_saved"], i["hourly_cost"], i.get("adoption", 1.0))
    llm = annual_llm_cost(i["tasks_per_month"], i["in_tokens"], i["out_tokens"], i["price_in_mtok"],
                          i["price_out_mtok"], i.get("calls_per_task", 1))
    run = llm + i.get("annual_platform_cost", 0)
    net = savings - run
    one_time = i.get("one_time_cost", 0)
    first_year_cost = one_time + run
    roi = (net - one_time) / first_year_cost * 100 if first_year_cost else math.inf
    pb = payback_months(one_time, net / 12)
    return {
        "annual_savings": round(savings, 2),
        "annual_llm_cost": round(llm, 2),
        "annual_run_cost": round(run, 2),
        "annual_net": round(net, 2),
        "roi_pct": round(roi, 2),
        "payback_months": pb if math.isinf(pb) else round(pb, 2),
    }


def sensitivity(inputs: dict, param, multipliers) -> list[tuple[float, float]]:
    params = (param,) if isinstance(param, str) else tuple(param)
    rows = []
    for m in multipliers:
        varied = {**inputs, **{p: inputs[p] * m for p in params}}
        rows.append((m, roi_summary(**varied)["annual_net"]))
    return rows
