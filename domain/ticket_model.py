from dataclasses import dataclass, field, asdict
from typing import List, Literal, Any, Dict

TicketType = Literal["bug", "data", "request", "unknown"]
Severity = Literal["low", "medium", "high"]

@dataclass
class Ticket:
    title: str = "미확인"
    module: str = "미확인"
    type: TicketType = "unknown"
    severity: Severity = "medium"
    summary: str = "미확인"
    repro_steps: List[str] = field(default_factory=lambda: ["미확인"])
    expected: str = "미확인"
    actual: str = "미확인"
    checkpoints: List[str] = field(default_factory=lambda: ["미확인"])
    questions: List[str] = field(default_factory=lambda: ["미확인"])
    sanitized: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Ticket":
        # dict -> Ticket (유연하게)
        return Ticket(
            title=str(d.get("title", "미확인") or "미확인"),
            module=str(d.get("module", "미확인") or "미확인"),
            type=d.get("type", "unknown") or "unknown",
            severity=d.get("severity", "medium") or "medium",
            summary=str(d.get("summary", "미확인") or "미확인"),
            repro_steps=list(d.get("repro_steps", []) or []),
            expected=str(d.get("expected", "미확인") or "미확인"),
            actual=str(d.get("actual", "미확인") or "미확인"),
            checkpoints=list(d.get("checkpoints", []) or []),
            questions=list(d.get("questions", []) or []),
            sanitized=bool(d.get("sanitized", True)),
        )
