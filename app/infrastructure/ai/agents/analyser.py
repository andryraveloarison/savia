# app/infrastructure/ai/agents/analyser.py

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from app.infrastructure.ai.agents.base import BaseAgent
from app.infrastructure.ai.base import BaseAIClient
from app.core.config import get_settings
from app.domain.entities.ticket import TicketEntity

logger = logging.getLogger("savia")

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
UNIFIED_ANALYSER_PROMPT = (_PROMPTS_DIR / "analyser.prompt").read_text(encoding="utf-8")


class AnalyserAgent(BaseAgent, BaseAIClient):
    """
    Agent Unifié: Gère la classification ET le diagnostic.
    """
    def __init__(self):
        BaseAgent.__init__(self, "AnalyserAgent")
        BaseAIClient.__init__(self)

    async def process(
        self, 
        ticket: TicketEntity, 
        doc_chunks: List[str]
    ) -> Dict[str, Any]:
        """
        Analyse complète du ticket avec ou sans documentation.
        """
        settings = get_settings()
        context_docs = "\n\n".join(doc_chunks) if doc_chunks else "AUCUNE DOCUMENTATION TROUVÉE POUR CETTE RÉFÉRENCE."
        
        prompt_user = f"""
### TICKET :
Message: {ticket.message}
Référence: {ticket.product_reference or 'Inconnue'}
Type: {ticket.problem_type or 'Non spécifié'}

### DOCUMENTATION TECHNIQUE :
{context_docs}
"""

        payload = {
            "model": settings.ollama_model,
            "messages": [
                {"role": "system", "content": UNIFIED_ANALYSER_PROMPT},
                {"role": "user", "content": prompt_user}
            ],
            "temperature": 0.2,
        }

        try:
            data = await self.post(payload)
            raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            cleaned = self._clean_json(raw)
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"[{self.name}] Erreur : {e}")
            return self._fallback_response(str(e))

    def _clean_json(self, raw: str) -> str:
        cleaned = raw.strip()
        if cleaned.startswith("```json"): cleaned = cleaned[7:].strip()
        elif cleaned.startswith("```"): cleaned = cleaned[3:].strip()
        if cleaned.endswith("```"): cleaned = cleaned[:-3].strip()
        return cleaned

    def _fallback_response(self, error: str) -> Dict[str, Any]:
        return {
            "category": "other", "urgency": "medium", "action": "escalate_to_human",
            "confidence_score": 0.0, "justifications": [f"Erreur technique : {error}"],
            "message_ia": "Une erreur technique est survenue. Un conseiller va prendre le relais."
        }
