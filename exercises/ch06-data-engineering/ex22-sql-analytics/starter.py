import sqlite3

TICKETS_PER_STATUS = ""
AVG_RESOLUTION_HOURS = ""
TOP_AGENTS = ""
REOPEN_RATE = ""
CUSTOMERS_WITHOUT_TICKETS = ""
WEEKLY_FLOW = ""


def tickets_per_status(conn: sqlite3.Connection):
    raise NotImplementedError


def avg_resolution_hours(conn):
    raise NotImplementedError


def top_agents(conn, as_of: str, days: int = 30, n: int = 3):
    raise NotImplementedError


def reopen_rate(conn):
    raise NotImplementedError


def customers_without_tickets(conn):
    raise NotImplementedError


def weekly_flow(conn):
    raise NotImplementedError
