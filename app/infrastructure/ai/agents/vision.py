# app/infrastructure/ai/agents/vision.py

import logging
from typing import Dict, Any
from app.infrastructure.ai.agents.base import BaseAgent
from app.infrastructure.ai.vision_adapter import VisionAdapter

logger = logging.getLogger("savia")

class VisionAgent(BaseAgent):
    """
    Agent 1: Responsable de l'analyse visuelle via LLM.
    Enrobe l'ancien VisionAdapter.
    """
    def __init__(self, vision_adapter: VisionAdapter):
        super().__init__("VisionAgent")
        self.adapter = vision_adapter

    async def process(self, image_base64: str) -> Dict[str, Any]:
        """
        Détecte la référence produit via le LLM Vision.
        """
        logger.info(f"[{self.name}] Analyse de l'image en cours...")
        return await self.adapter.detect_product_reference(image_base64)
 