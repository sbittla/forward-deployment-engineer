"""Value model the CMO and CFO both signed off on."""


def roi(calls_per_month: int, minutes_saved_per_call: float, nurse_hourly_cost: float,
        monthly_platform_cost: float, one_time_cost: float) -> dict:
    hours = calls_per_month * minutes_saved_per_call / 60
    gross = hours * nurse_hourly_cost
    net = gross - monthly_platform_cost
    return {
        "nurse_hours_saved_per_month": round(hours, 1),
        "net_savings_per_month": round(net, 2),
        "payback_months": round(one_time_cost / net, 1) if net > 0 else None,
    }
