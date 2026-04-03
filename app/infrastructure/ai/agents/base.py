# app/infrastructure/ai/agents/base.py

from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):
    """
    Classe de base pour tous les agents spécialisés.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def process(self, *args, **kwargs) -> Any:
        pass
