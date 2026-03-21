import httpx
import json
import logging
from app.domain.entities.ticket import TicketEntity
from app.domain.entities.ai_result import AIAnalysisResult
from app.domain.types.enums import Category, Urgency, Action
from app.infrastructure.ai.base import AIClient

logger = logging.getLogger("savia")

class OllamaClient(AIClient):
    def __init__(self, base_url: str, model: str = "llama3"):
        self.base_url = base_url
        self.model = model

    async def analyze_ticket(self, ticket: TicketEntity) -> AIAnalysisResult:
        url = f"{self.base_url}/api/generate"
        
        prompt = f"""
        Analyze the following maintenance ticket and return JSON:
        Message: {ticket.message}
        Equipment: {ticket.equipment.type} ({ticket.equipment.model})
        
        JSON structure:
        {{
            "category": "heating|plumbing|electrical|ventilation|other",
            "urgency": "low|medium|high|critical",
            "action": "auto_resolution|request_additional_info|schedule_intervention|generate_quote|escalate_to_human",
            "confidence": 0.0-1.0,
            "justification": ["fact 1", "fact 2"]
        }}
        """
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Parsing simple de la réponse JSON du modèle
                content = json.loads(data["response"])
                
                return AIAnalysisResult(
                    category=Category(content.get("category", "other")),
                    urgency=Urgency(content.get("urgency", "low")),
                    action=Action(content.get("action", "escalate_to_human")),
                    confidence_score=float(content.get("confidence", 0.0)),
                    justifications=content.get("justification", []),
                    raw_response=data["response"]
                )
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            raise  # Let the service handle the fallback
