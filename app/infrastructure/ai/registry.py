# app/infrastructure/ai/registry.py

import logging
from typing import Optional

from app.infrastructure.ai.vision_adapter import VisionAdapter
from app.infrastructure.ai.analysis_adapter import AIAdapter
from app.infrastructure.ai.documentation_adapter import DocumentationAdapter
from app.infrastructure.ai.documentation_ai_adapter import DocumentationAIAdapter

logger = logging.getLogger("savia")

class AIRegistry:
    """
    Registre centralisé pour les adaptateurs d'intelligence artificielle.
    Implémente le pattern Singleton pour garantir une instance unique de chaque adaptateur.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIRegistry, cls).__new__(cls)
            cls._instance._vision_adapter = None
            cls._instance._ai_adapter = None
            cls._instance._doc_adapter = None
            cls._instance._doc_ai_adapter = None
        return cls._instance

    @property
    def vision(self) -> VisionAdapter:
        if self._vision_adapter is None:
            logger.info("🔌 Initialisation de VisionAdapter...")
            self._vision_adapter = VisionAdapter()
        return self._vision_adapter

    @property
    def ai(self) -> AIAdapter:
        if self._ai_adapter is None:
            logger.info("🔌 Initialisation de AIAdapter...")
            self._ai_adapter = AIAdapter()
        return self._ai_adapter

    @property
    def documentation(self) -> DocumentationAdapter:
        if self._doc_adapter is None:
            logger.info("🔌 Initialisation de DocumentationAdapter...")
            self._doc_adapter = DocumentationAdapter()
        return self._doc_adapter

    @property
    def documentation_ai(self) -> DocumentationAIAdapter:
        if self._doc_ai_adapter is None:
            logger.info("🔌 Initialisation de DocumentationAIAdapter...")
            self._doc_ai_adapter = DocumentationAIAdapter()
        return self._doc_ai_adapter

# Instance globale pour un accès facile
ai_registry = AIRegistry()
