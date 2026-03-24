from abc import ABC, abstractmethod
from app.domain.entities.ticket import TicketEntity
from app.domain.entities.ai_result import AIAnalysisResult

class AIClient(ABC):
    @abstractmethod
    async def analyze_ticket(self, ticket: TicketEntity) -> AIAnalysisResult:
        """
        Analyse un ticket via un LLM.
        """
        ...  # pragma: no cover 