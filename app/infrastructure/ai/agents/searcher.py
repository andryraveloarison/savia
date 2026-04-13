# app/infrastructure/ai/agents/searcher.py

import logging
from typing import List, Dict, Any
from app.infrastructure.ai.agents.base import BaseAgent
from app.infrastructure.ai.documentation_adapter import DocumentationAdapter

logger = logging.getLogger("savia")

class SearcherAgent(BaseAgent):
    """
    Agent 2: Responsable de la recherche documentaire (Local / FAISS).
    NE contient AUCUN appel LLM.
    """
    def __init__(self, doc_adapter: DocumentationAdapter):
        super().__init__("SearcherAgent")
        self.doc_adapter = doc_adapter

    async def process(
        self, 
        category: str, 
        product_ref: str,  
        user_message: str = "", 
        top_k: int = 5
    ) -> List[str]:
        """
        Interroge l'index FAISS local.
        """
        logger.info(f"[{self.name}] Recherche doc pour {category} / {product_ref}")
        
        if not category or not product_ref:
            logger.warning(f"[{self.name}] Catégorie ou référence manquante pour la recherche.")
            return []

        try:
            chunks = self.doc_adapter.query(
                category=category,
                product_ref=product_ref,
                user_message=user_message,
                top_k=top_k
            )
            return chunks
        except Exception as e:
            logger.error(f"[{self.name}] Erreur recherche FAISS : {e}")
            return []
