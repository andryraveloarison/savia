import logging
from app.domain.entities.ticket import TicketEntity
from app.domain.entities.ai_result import AIAnalysisResult
from app.domain.types.enums import Category, Urgency, Action
from app.infrastructure.ai.base import AIClient

logger = logging.getLogger("savia")

class AIAdapter(AIClient):
    """
    Adaptateur AI (mockable) pour l'analyse des tickets.
    """
    async def analyze_ticket(self, ticket: TicketEntity) -> AIAnalysisResult:
        # Implémentation par défaut (similaire au MockAIClient précédent)
        # Permet d'avoir une structure prête pour une future intégration réelle.
        message = ticket.message.lower()
        
        if "fuite" in message or "inondation" in message:
            return AIAnalysisResult(
                category=Category.PLUMBING,
                urgency=Urgency.CRITICAL,
                action=Action.SCHEDULE_INTERVENTION,
                confidence_score=0.95,
                justifications=["Urgence détectée par l'AIAdapter (Plomberie)"],
                raw_response='{"status": "detected", "type": "leak"}'
            )

        return AIAnalysisResult(
            category=Category.OTHER,
            urgency=Urgency.LOW,
            action=Action.ESCALATE_TO_HUMAN,
            confidence_score=0.5,
            justifications=["Analyse AIAdapter : situation ambiguë"],
            raw_response='{"status": "unknown"}'
        )
