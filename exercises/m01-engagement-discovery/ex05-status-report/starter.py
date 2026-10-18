from datetime import date


def overall_status(tasks: list[dict], today: date) -> str:
    raise NotImplementedError


def render(tasks: list[dict], today: date, project: str) -> str:
    raise NotImplementedError
