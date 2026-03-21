from app.domain.entities.ticket import TicketEntity
from app.domain.entities.ai_result import AIAnalysisResult
from app.domain.types.enums import Category, Urgency, Action
from app.infrastructure.ai.base import AIClient

class MockAIClient(AIClient):
    async def analyze_ticket(self, ticket: TicketEntity) -> AIAnalysisResult:
        """
        Simulation d'une analyse IA déterministe pour tests.
        """
        # Simulation d'un délai
        import asyncio
        await asyncio.sleep(0.1)
        
        message = ticket.message.lower()
        
        if "fuite" in message or "inondation" in message:
            return AIAnalysisResult(
                category=Category.PLUMBING,
                urgency=Urgency.CRITICAL,
                action=Action.SCHEDULE_INTERVENTION,
                confidence_score=0.95,
                justifications=["Detection of plumbing emergency keywords", "Inundation risk handled by AI"],
                raw_response='{"category": "plumbing", "urgency": "critical"}'
            )
            
        return AIAnalysisResult(
            category=Category.OTHER,
            urgency=Urgency.LOW,
            action=Action.ESCALATE_TO_HUMAN,
            confidence_score=0.5,
            justifications=["Message ambiguous or unknown situation"],
            raw_response='{"category": "other", "urgency": "low"}'
        )
