# app/infrastructure/ai/documentation_ai_adapter.py

import json
import logging
from typing import List, Dict, Any

from app.core.config import get_settings
from app.infrastructure.ai.base import BaseAIClient

logger = logging.getLogger("savia")


DOCUMENTATION_AI_PROMPT = """
Tu es un assistant SAV technique. Tu dois aider l'utilisateur UNIQUEMENT en utilisant les informations extraites de la documentation fournie.

STRICTES CONSIGNES DE SÉCURITÉ :
1. NE JAMAIS INVENTER de sens pour un code erreur ou un problème qui n'est pas EXPLICITEMENT listé dans la documentation fournie.
2. SI LE PROBLÈME OU LE CODE ERREUR N'EST PAS DANS LA DOCUMENTATION :
   - "confidence_score": 0.1
   - "recommended_actions": []
   - "diagnostic_help": "Ce code erreur ou ce problème n'est pas répertorié dans la documentation technique."
3. NE PAS UTILISER tes connaissances générales pour deviner. Reste factuel vis-à-vis du contexte.

### EXEMPLES DE RÉPONSES ATTENDUES :

**Exemple 1 (Problème trouvé) :**
User: "Mon radiateur affiche E02"
Context: "Code E02 : Surchauffe. Solution : Laisser refroidir."
Response:
{
  "product_reference": "RFLC",
  "diagnostic_help": "Le code E02 indique une surchauffe de l'appareil.",
  "recommended_actions": ["Éteindre l'appareil", "Le laisser refroidir 30 minutes", "Redémarrer"],
  "important_warnings": ["Ne pas couvrir l'appareil"],
  "confidence_score": 0.95
}

**Exemple 2 (Problème NON trouvé) :**
User: "Mon radiateur affiche E999"
Context: "Codes: E01, E02, E03"
Response:
{
  "product_reference": "RFLC",
  "diagnostic_help": "Le code erreur E999 n'est pas répertorié dans la documentation technique.",
  "recommended_actions": [],
  "important_warnings": [],
  "confidence_score": 0.1
}

Réponds uniquement en JSON.
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
        user_message: str = "",
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
Problème de l'utilisateur: {user_message}

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