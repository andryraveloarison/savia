# app/infrastructure/ai/ollama_adapter.py

import json
from app.core.config import get_settings
from app.domain.entities.ai_result import AIAnalysisResult
from app.infrastructure.ai.base import BaseAIClient


SYSTEM_PROMPT = """
Tu es un moteur d'analyse SAV pour équipements de chauffage.

Analyse le ticket, le type de problème et la référence produit.

Règles de décision :
1. Si l'utilisateur n'a pas mis assez d'informations pour diagnostiquer (ex: message trop court, manque de détails sur la panne) :
   - action : "request_additional_info"
   - confidence_score : très élevé (typiquement entre 0.90 et 1.0) car tu es certain du manque d'informations. Ajuste selon ton degré de certitude.
   - message_ia : Demande précisément ce qui manque (ex: "Veuillez prendre une photo de la plaque signalétique sur votre appareil").
2. Si les informations sont complètes mais qu'AUCUN document n'a été trouvé pour cette référence :
   - action : "escalate_to_human"
   - confidence_score : bas (entre 0.1 et 0.4) si tu es sûr qu'aucune documentation n'est disponible.
   - justifications : Préciser qu'aucune documentation n'est disponible.
3. Si le problème nécessite obligatoirement une intervention physique (ex: fuite d'eau importante, odeur de gaz, court-circuit) :
   - action : "schedule_intervention"
   - message_ia : "Une intervention d'un technicien est nécessaire pour résoudre ce problème."
4. Si c'est très urgent ET que tu n'es pas sûr de la solution :
   - action : "escalate_to_human"
5. Sinon, propose une résolution automatique si possible.

Réponds uniquement en JSON.

CONSIGNES IMPORTANTES POUR "message_ia" :
- Ce champ est UNIQUEMENT destiné à la communication (ex: salutation, demande de précision).
- NE JAMAIS donner de conseils techniques, NE JAMAIS expliquer un code erreur, NE JAMAIS proposer de réparation.
- Si le ticket est incomplet, demande poliment ce qui manque.
- Si le ticket est complet, laisse "message_ia" vide ou mets un simple message d'accueil.

{
  "category": "<heating|plumbing|electrical|ventilation|other>",
  "urgency": "<critical|high|medium|low>",
  "action": "<auto_resolution|request_additional_info|schedule_intervention|generate_quote|escalate_to_human>",
  "confidence_score": <float entre 0.0 et 1.0>,
  "justifications": ["..."],
  "message_ia": "<message de communication uniquement, pas de technique>"
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

    async def analyze_ticket(self, ticket, has_documentation: bool = False) -> AIAnalysisResult:
        settings = get_settings()

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
Ticket:
{ticket.message}

Type de problème:
{ticket.problem_type or "Non spécifié"}

Référence produit:
{ticket.product_reference or "Inconnue"}

Documentation trouvée: {"Oui" if has_documentation else "Non"}
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
                message_ia=parsed.get("message_ia"),
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