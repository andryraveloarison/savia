from datetime import datetime, timezone
from app.domain.types.enums import DecisionType, Action
from app.core.config import get_settings
from app.shared.types.version import VersionStr

settings = get_settings()

class AuditService: 
    @staticmethod
    def run(action: Action, confidence_score: float) -> dict:
        if confidence_score < settings.confidence_threshold_escalate or action == Action.ESCALATE_TO_HUMAN:
            decision_type = DecisionType.HUMAN_ESCALATED
        else:
            decision_type = DecisionType.AI_ASSISTED

        return {
            "analyzed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "engine_version": settings.engine_version,
            "decision_type": decision_type.value,
        }
