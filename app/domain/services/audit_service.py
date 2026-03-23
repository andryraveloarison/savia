from datetime import datetime, timezone
from app.domain.types.enums import DecisionType, Action
from app.core.config import get_settings
from app.shared.types.version import VersionStr

settings = get_settings()

class AuditService: 
    @staticmethod
    def run(provider: str) -> dict:
        return {
            "analyzed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "engine_version": settings.engine_version,
            "decision_type": provider,
        }
