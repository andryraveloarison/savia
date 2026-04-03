# app/infrastructure/ai/registry.py

import logging
from typing import Optional

from app.infrastructure.ai.vision_adapter import VisionAdapter
from app.infrastructure.ai.documentation_adapter import DocumentationAdapter

# New Agents
from app.infrastructure.ai.agents.vision import VisionAgent
from app.infrastructure.ai.agents.searcher import SearcherAgent
from app.infrastructure.ai.agents.analyser import AnalyserAgent

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
            cls._instance._doc_adapter = None
            
            # Agents
            cls._instance._agent_vision = None
            cls._instance._agent_searcher = None
            cls._instance._agent_analyser = None
        return cls._instance

    @property
    def vision(self) -> VisionAdapter:
        if self._vision_adapter is None:
            logger.info("🔌 Initialisation de VisionAdapter...")
            self._vision_adapter = VisionAdapter()
        return self._vision_adapter

    @property
    def documentation(self) -> DocumentationAdapter:
        if self._doc_adapter is None:
            logger.info("🔌 Initialisation de DocumentationAdapter...")
            self._doc_adapter = DocumentationAdapter()
        return self._doc_adapter

    # --- Nouveaux Agents ---

    @property
    def vision_agent(self) -> VisionAgent:
        if self._agent_vision is None:
            self._agent_vision = VisionAgent(self.vision)
        return self._agent_vision

    @property
    def searcher_agent(self) -> SearcherAgent:
        if self._agent_searcher is None:
            self._agent_searcher = SearcherAgent(self.documentation)
        return self._agent_searcher

    @property
    def analyser_agent(self) -> AnalyserAgent:
        if self._agent_analyser is None:
            self._agent_analyser = AnalyserAgent()
        return self._agent_analyser

# Instance globale pour un accès facile
ai_registry = AIRegistry()
