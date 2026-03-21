"""
Configuration globale de l'application Savia.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from app.shared.types.version import VersionStr

class Settings(BaseSettings):
    app_name: str = "Savia — Moteur d'aide à la décision SAV"
    app_version: VersionStr = "1.0.0"
    debug: bool = False
    engine_version: VersionStr = "savia-mvp-v1"
    confidence_threshold_escalate: float = 0.40
    confidence_threshold_auto: float = 0.85
    
    # AI Settings
    ai_enabled: bool = True
    ai_provider: str = "mock"  # "mock" or "ollama"
    ollama_url: str = "http://localhost:11434"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
