import json
import httpx
import logging
from app.core.config import get_settings
from app.domain.entities.ai_result import AIAnalysisResult

logger = logging.getLogger("savia")

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


class AIAdapter:
    async def analyze_ticket(self, ticket):
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

        headers = {
            "Authorization": f"Bearer {settings.ollama_api_key}",
            "Content-Type": "application/json",
        }

        try:
            timeout = httpx.Timeout(60.0, connect=20.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    settings.ollama_host + "/chat/completions",
                    json=payload,
                    headers=headers,
                )

            response.raise_for_status()

            data = response.json()
            raw = data["choices"][0]["message"]["content"]
            parsed = json.loads(raw)

            return AIAnalysisResult(
                category=parsed["category"],
                urgency=parsed["urgency"],
                action=parsed["action"],
                confidence_score=parsed["confidence_score"],
                justifications=parsed["justifications"],
                raw_response=raw,
            )

        except httpx.ReadTimeout:
            logger.error("LLM timeout")
            raise Exception("LLM timeout")

        except httpx.ConnectError:
            logger.error("Connexion Ollama impossible")
            raise Exception("Connexion Ollama impossible")

        except json.JSONDecodeError:
            logger.error("JSON invalide retourné par le LLM")
            raise Exception("JSON invalide")

        except Exception as e:
            logger.exception("Erreur AIAdapter")
            raise e