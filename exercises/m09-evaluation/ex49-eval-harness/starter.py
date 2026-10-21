from dataclasses import dataclass, field


@dataclass
class Case:
    id: str
    input: str
    expected: object
    grader: str
    tags: list[str] = field(default_factory=list)


@dataclass
class CaseResult:
    case: Case
    passed: bool
    output: str
    error: str = ""


@dataclass
class EvalReport:
    results: list[CaseResult]

    @property
    def pass_rate(self) -> float:
        raise NotImplementedError

    def by_tag(self) -> dict[str, float]:
        raise NotImplementedError

    def failures(self) -> list[CaseResult]:
        raise NotImplementedError

    def to_markdown(self) -> str:
        raise NotImplementedError

    def by_slice(self, z: float = 1.96) -> dict[str, dict]:
        raise NotImplementedError

    def failure_taxonomy(self, labels: dict[str, str]) -> list[tuple[str, int]]:
        raise NotImplementedError


GRADERS: dict = {}


def load_cases(path) -> list[Case]:
    raise NotImplementedError


def run_eval(cases: list[Case], system) -> EvalReport:
    raise NotImplementedError


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    raise NotImplementedError


def cost_per_success(cost_per_request: float, pass_rate: float) -> float:
    raise NotImplementedError


def find_leakage(cases: list[Case], examples: list[str]) -> list[str]:
    raise NotImplementedError
