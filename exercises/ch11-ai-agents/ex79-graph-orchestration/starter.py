from dataclasses import dataclass, field

END = "__end__"


@dataclass
class Result:
    state: dict
    status: str               # "done" | "interrupted"
    steps: int = 0
    next: str | None = None


class MemoryCheckpointer:
    def __init__(self):
        self._store: dict[str, list[dict]] = {}

    def put(self, thread_id: str, checkpoint: dict) -> None:
        raise NotImplementedError

    def latest(self, thread_id: str) -> dict:
        raise NotImplementedError

    def history(self, thread_id: str) -> list[dict]:
        raise NotImplementedError


class StateGraph:
    def __init__(self, reducers: dict | None = None):
        self.reducers = reducers or {}

    def add_node(self, name: str, fn) -> None:
        raise NotImplementedError

    def add_edge(self, src: str, dst: str) -> None:
        raise NotImplementedError

    def add_conditional_edges(self, src: str, router) -> None:
        raise NotImplementedError

    def set_entry_point(self, name: str) -> None:
        raise NotImplementedError

    def compile(self, checkpointer=None, interrupt_before=(), max_steps: int = 25):
        raise NotImplementedError
