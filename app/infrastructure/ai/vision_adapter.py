# app/infrastructure/ai/vision_adapter.py

import json
import logging
from app.core.config import get_settings
from app.infrastructure.ai.base import BaseAIClient

logger = logging.getLogger("savia")

VISION_PROMPT = """
Tu es un agent de reconnaissance produit.
Analyse l'image et identifie la référence produit.

Réponds uniquement en JSON :

{
  "product_reference": "<reference ou unknown>",
  "confidence": <float>
}
"""


class VisionAdapter(BaseAIClient):
    """
    Adaptateur Ollama Vision pour l'analyse d'image produit.
    Utilise BaseAIClient pour gérer headers et requêtes HTTP.
    """

    async def detect_product_reference(self, image_base64: str):
        messages = [
            {"role": "system", "content": VISION_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyse cette image"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        },
                    },
                ],
            },
        ]

        payload = {
            "model": get_settings().ollama_vision_model,
            "messages": messages,
        }

        try:
            # Appel via BaseAIClient
            data = await self.post(payload)

            # Extraction du contenu
            raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not raw:
                logger.error("Vision LLM a renvoyé une réponse vide")
                return {"product_reference": "unknown", "confidence": 0.0, "error": "empty_response"}

            # Nettoyage des backticks ```json ... ```
            cleaned = raw.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[len("```json"):].strip()
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()

            # Parsing JSON défensif
            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError:
                logger.error("Réponse JSON invalide après nettoyage")
                return {"product_reference": "unknown", "confidence": 0.0, "error": "invalid_json"}

            # Retour du résultat
            return {
                "product_reference": parsed.get("product_reference", "unknown"),
                "confidence": float(parsed.get("confidence", 0.0)),
            }

        except Exception as e:
            logger.exception("Erreur VisionAdapter")
            return {"product_reference": "unknown", "confidence": 0.0, "error": str(e)}