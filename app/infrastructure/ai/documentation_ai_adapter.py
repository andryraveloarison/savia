# app/infrastructure/ai/documentation_ai_adapter.py

import json
import logging
from typing import List, Dict, Any

from app.core.config import get_settings
from app.infrastructure.ai.base import BaseAIClient

logger = logging.getLogger("savia")


DOCUMENTATION_AI_PROMPT = """
Tu es un assistant SAV pour équipements de chauffage.

Tu dois aider un utilisateur à résoudre un problème en utilisant la documentation produit.

Ta réponse doit être un message clair pour un client non technique.

Réponds uniquement en JSON :

{
  "problem": "<problème identifié>",
  "message": "<message complet formaté avec étapes et avertissements>",
  "confidence_score": <float>
}

Le message doit être formaté comme :

**Problème identifié : ...**

**Étapes à suivre :**
1. ...
2. ...
3. ...

⚠️ **Avertissements :**
- ...
"""


def clean_llm_json(raw: str) -> str:
    """
    Nettoie la réponse LLM pour enlever les ```json et ``` encadrants.
    """
    cleaned = raw.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned


class DocumentationAIAdapter(BaseAIClient):
    """
    Utilise les chunks de documentation (RAG) pour générer
    une aide technique exploitable par un technicien SAV.
    """

    async def analyze_documentation(
        self,
        category: str,
        product_reference: str,
        doc_chunks: List[str],
    ) -> Dict[str, Any]:

        if not doc_chunks:
            return {
                "product_reference": product_reference,
                "diagnostic_help": "",
                "recommended_actions": [],
                "important_warnings": [],
                "confidence_score": 0.0,
                "error": "no_documentation_found",
            }

        try:
            # 🔹 Limiter taille (éviter explosion tokens)
            max_chars = 12000
            context = "\n\n".join(doc_chunks)
            context = context[:max_chars]

            messages = [
                {"role": "system", "content": DOCUMENTATION_AI_PROMPT},
                {
                    "role": "user",
                    "content": f"""
Produit: {product_reference}
Catégorie: {category}

Documentation:
{context}
"""
                },
            ]

            payload = {
                "model": get_settings().ollama_model,
                "messages": messages,
            }

            # 🔹 Appel LLM via BaseAIClient
            data = await self.post(payload)

            raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not raw:
                logger.error("Réponse vide du DocumentationAI LLM")
                return self._fallback(product_reference, "empty_response")

            cleaned = clean_llm_json(raw)

            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError:
                logger.error("JSON invalide du DocumentationAI LLM")
                return {
                    **self._fallback(product_reference, "invalid_json"),
                    "raw_response": raw,
                }

            # 🔹 Normalisation sortie
            return {
                "product_reference": parsed.get("product_reference", product_reference),
                "diagnostic_help": parsed.get("diagnostic_help", ""),
                "recommended_actions": parsed.get("recommended_actions", []),
                "important_warnings": parsed.get("important_warnings", []),
                "confidence_score": float(parsed.get("confidence_score", 0.0)),
                "raw_response": raw,
            }

        except Exception as e:
            logger.exception("Erreur DocumentationAIAdapter")
            return self._fallback(product_reference, str(e))

    def _fallback(self, product_reference: str, error: str) -> Dict[str, Any]:
        """
        Réponse par défaut en cas d'erreur
        """
        return {
            "product_reference": product_reference,
            "diagnostic_help": "",
            "recommended_actions": [],
            "important_warnings": [],
            "confidence_score": 0.0,
            "error": error,
        }