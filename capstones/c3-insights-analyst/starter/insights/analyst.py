"""NL-to-SQL analyst with a repair loop. Numbers in the narrative come from the query result, never the model."""
import re
import sqlite3
from dataclasses import dataclass, field

from .semantic import schema_prompt
from .sqlguard import UnsafeSQL, guard_sql

REFUSAL = "I can't answer that with the data and permissions I have. A data analyst can help."


@dataclass
class Answer:
    question: str
    sql: str = ""
    columns: list[str] = field(default_factory=list)
    rows: list[tuple] = field(default_factory=list)
    narrative: str = ""
    attempts: int = 0
    refused: bool = False
    errors: list[str] = field(default_factory=list)


def extract_sql(text: str) -> str:
    raise NotImplementedError


def narrate(columns: list[str], rows: list[tuple]) -> str:
    raise NotImplementedError


class Analyst:
    def __init__(self, llm, conn: sqlite3.Connection, max_attempts: int = 3, model: str = "claude-sonnet-5-5"):
        self.llm, self.conn, self.max_attempts, self.model = llm, conn, max_attempts, model
        self.system = (
            "You write a single read-only SQLite SELECT query that answers the user's question.\n"
            f"{schema_prompt(conn)}\n"
            "Reply with only the SQL in a ```sql block. If the question cannot be answered with these tables, "
            "or asks to change data, reply exactly: CANNOT_ANSWER"
        )

    def ask(self, question: str) -> Answer:
        raise NotImplementedError
