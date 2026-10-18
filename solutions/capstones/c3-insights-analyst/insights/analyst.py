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
    m = re.search(r"```(?:sql)?\s*(.*?)```", text, re.S | re.I)
    return (m.group(1) if m else text).strip()


def narrate(columns: list[str], rows: list[tuple]) -> str:
    if not rows:
        return "The query returned no rows."
    if len(rows) == 1 and len(columns) == 1:
        return f"{columns[0]}: {rows[0][0]}"
    first = ", ".join(f"{c}={v}" for c, v in zip(columns, rows[0]))
    return f"{len(rows)} rows. First row: {first}."


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
        ans = Answer(question)
        messages = [{"role": "user", "content": question}]
        for attempt in range(1, self.max_attempts + 1):
            ans.attempts = attempt
            reply = self.llm.complete(list(messages), system=self.system, model=self.model).text
            if reply.strip() == "CANNOT_ANSWER":
                break
            sql = extract_sql(reply)
            try:
                safe = guard_sql(sql)
                cur = self.conn.execute(safe)
                ans.sql, ans.rows = safe, cur.fetchall()
                ans.columns = [d[0] for d in cur.description]
                ans.narrative = narrate(ans.columns, ans.rows)
                return ans
            except (UnsafeSQL, sqlite3.Error) as e:
                err = f"{type(e).__name__}: {e}"
                ans.errors.append(err)
                messages += [{"role": "assistant", "content": reply},
                             {"role": "user", "content": f"That query failed ({err}). Fix it, or reply CANNOT_ANSWER."}]
        ans.refused, ans.narrative = True, REFUSAL
        return ans
