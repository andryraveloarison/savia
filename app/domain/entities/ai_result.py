from dataclasses import dataclass, field
from app.domain.types.enums import Category, Urgency, Action

@dataclass(frozen=True)
class AIAnalysisResult:
    category: Category | None = None
    urgency: Urgency | None = None
    action: Action | None = None
    confidence_score: float = 0.0
    justifications: list[str] = field(default_factory=list)
    raw_response: str | None = None
