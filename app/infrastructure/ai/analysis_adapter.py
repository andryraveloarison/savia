# app/infrastructure/ai/ollama_adapter.py

import json
from app.core.config import get_settings
from app.domain.entities.ai_result import AIAnalysisResult
from app.infrastructure.ai.base import BaseAIClient


SYSTEM_PROMPT = """
Tu es un moteur d'analyse SAV.

Analyse le ticket et la référence produit.

Réponds uniquement en JSON :

{
  "category": "<plumbing|electrical|heating|ventilation>",
  "urgency": "<critical|high|medium|low>",
  "action": "<schedule_intervention|escalate_to_human|request_additional_info|generate_quote>",
  "confidence_score": <float>,
  "justifications": ["..."]
}
"""


def clean_llm_json(raw: str) -> str:
    """
    Nettoie la réponse LLM pour enlever les ```json et ``` encadrant.
    """
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()
    return cleaned


class AIAdapter(BaseAIClient):
    """
    Adaptateur Ollama pour l'analyse des tickets.
    Utilise BaseAIClient pour gérer l'authentification et les requêtes HTTP.
    """

    async def analyze_ticket(self, ticket) -> AIAnalysisResult:
        settings = get_settings()

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
Ticket:
{ticket.message}

Référence produit:
{ticket.product_reference}
"""
            },
        ]

        payload = {
            "model": settings.ollama_model,
            "messages": messages,
        }

        try:
            # Appel via BaseAIClient
            data = await self.post(payload)

            # Extraction et nettoyage de la réponse LLM
            raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not raw:
                return AIAnalysisResult(
                    category="other",
                    urgency="low",
                    action="escalate_to_human",
                    confidence_score=0.0,
                    justifications=["Erreur : réponse vide du LLM"],
                    raw_response=None,
                )

            cleaned = clean_llm_json(raw)

            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError:
                return AIAnalysisResult(
                    category="other",
                    urgency="low",
                    action="escalate_to_human",
                    confidence_score=0.0,
                    justifications=["Erreur : JSON invalide du LLM"],
                    raw_response=raw,
                )

            # Retour du résultat
            return AIAnalysisResult(
                category=parsed.get("category", "other"),
                urgency=parsed.get("urgency", "low"),
                action=parsed.get("action", "escalate_to_human"),
                confidence_score=float(parsed.get("confidence_score", 0.0)),
                justifications=parsed.get("justifications", []),
                raw_response=raw,
            )

        except Exception as exc:
            return AIAnalysisResult(
                category="other",
                urgency="low",
                action="escalate_to_human",
                confidence_score=0.0,
                justifications=[f"Erreur lors de l'appel LLM : {exc}"],
                raw_response=None,
            )