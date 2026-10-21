def funnel(events: list[dict]) -> dict:
    raise NotImplementedError


def weekly_retention(events: list[dict], cohort_week: int) -> list[float]:
    raise NotImplementedError


def lagging_teams(events: list[dict], threshold: float = 0.5) -> list[tuple[str, float]]:
    raise NotImplementedError


def change_plan(lagging: list[tuple[str, float]]) -> list[str]:
    raise NotImplementedError


def diff_in_diff(pre_treat, post_treat, pre_ctrl, post_ctrl) -> dict:
    raise NotImplementedError
