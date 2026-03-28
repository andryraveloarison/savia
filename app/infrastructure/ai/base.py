from abc import ABC, abstractmethod
from app.domain.entities.ticket import TicketEntity
from app.domain.entities.ai_result import AIAnalysisResult

import json
import httpx
from app.core.config import get_settings


class BaseAIClient:
    def __init__(self):
        settings = get_settings()
        self.host = settings.ollama_host
        self.api_key = settings.ollama_api_key

    async def post(self, payload):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.host + "/chat/completions",
                json=payload,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            print("HTTP status:", response.status_code)
            print("Response text:", response.text)  # <- très important
            return response.json()