import copy
from dataclasses import dataclass, field

END = "__end__"


@dataclass
class Result:
    state: dict
    status: str
    steps: int = 0
    next: str | None = None


class MemoryCheckpointer:
    def __init__(self):
        self._store: dict[str, list[dict]] = {}

    def put(self, thread_id: str, checkpoint: dict) -> None:
        self._store.setdefault(thread_id, []).append(copy.deepcopy(checkpoint))

    def latest(self, thread_id: str) -> dict:
        return copy.deepcopy(self._store[thread_id][-1])

    def history(self, thread_id: str) -> list[dict]:
        return copy.deepcopy(self._store.get(thread_id, []))


class StateGraph:
    def __init__(self, reducers: dict | None = None):
        self.reducers = reducers or {}
        self.nodes: dict = {}
        self.edges: dict[str, str] = {}
        self.routers: dict = {}
        self.entry: str | None = None

    def add_node(self, name: str, fn) -> None:
        self.nodes[name] = fn

    def add_edge(self, src: str, dst: str) -> None:
        self.edges[src] = dst

    def add_conditional_edges(self, src: str, router) -> None:
        self.routers[src] = router

    def set_entry_point(self, name: str) -> None:
        self.entry = name

    def _validate(self):
        if self.entry is None:
            raise ValueError("no entry point")
        known = set(self.nodes) | {END}
        if self.entry not in self.nodes:
            raise ValueError(f"entry point {self.entry!r} is not a node")
        for src, dst in self.edges.items():
            if src not in self.nodes or dst not in known:
                raise ValueError(f"edge {src!r} -> {dst!r} references an unknown node")
        for n in self.nodes:
            if n in self.edges and n in self.routers:
                raise ValueError(f"node {n!r} has both a plain and a conditional edge")
            if n not in self.edges and n not in self.routers:
                raise ValueError(f"node {n!r} has no outgoing edge")
        reached, frontier = {self.entry}, [self.entry]
        while frontier:
            n = frontier.pop()
            nxt = set(self.nodes) if n in self.routers else {self.edges[n]} - {END}
            for m in nxt - reached:
                reached.add(m)
                frontier.append(m)
        unreachable = set(self.nodes) - reached
        if unreachable:
            raise ValueError(f"unreachable nodes: {sorted(unreachable)}")

    def compile(self, checkpointer=None, interrupt_before=(), max_steps: int = 25) -> "App":
        self._validate()
        return App(self, checkpointer, tuple(interrupt_before), max_steps)


class App:
    def __init__(self, graph: StateGraph, checkpointer, interrupt_before, max_steps):
        self.g, self.cp, self.interrupt_before, self.max_steps = graph, checkpointer, interrupt_before, max_steps

    def _apply(self, state: dict, update: dict) -> dict:
        out = dict(state)
        for k, v in (update or {}).items():
            out[k] = self.g.reducers[k](out[k], v) if k in self.g.reducers and k in out else v
        return out

    def _next(self, node: str, state: dict) -> str:
        return self.g.routers[node](state) if node in self.g.routers else self.g.edges[node]

    def _save(self, thread_id, state, nxt):
        if self.cp is not None and thread_id is not None:
            self.cp.put(thread_id, {"state": state, "next": nxt})

    def _run(self, state: dict, node: str, thread_id, skip_interrupt: bool) -> Result:
        steps = 0
        while node != END:
            if node in self.interrupt_before and not skip_interrupt:
                self._save(thread_id, state, node)
                return Result(state, "interrupted", steps, node)
            skip_interrupt = False
            steps += 1
            if steps > self.max_steps:
                raise RuntimeError(f"exceeded max_steps={self.max_steps}")
            state = self._apply(state, self.g.nodes[node](state))
            node = self._next(node, state)
            self._save(thread_id, state, node)
        return Result(state, "done", steps)

    def invoke(self, state: dict, thread_id: str | None = None) -> Result:
        return self._run(dict(state), self.g.entry, thread_id, skip_interrupt=False)

    def resume(self, thread_id: str, updates: dict | None = None) -> Result:
        cp = self.cp.latest(thread_id)
        state = self._apply(cp["state"], updates or {})
        return self._run(state, cp["next"], thread_id, skip_interrupt=True)
