"""
Configuration globale de l'application Savia.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from app.shared.types.version import VersionStr

class Settings(BaseSettings):
    app_name: str = "Savia — Moteur d'aide à la décision SAV"
    app_version: VersionStr = "1.4.0"
    debug: bool = False
    engine_version: VersionStr = "savia-mvp-v1"
    confidence_threshold_escalate: float = 0.7
    confidence_threshold_ai: float = 0.5
    
    ai_enabled: bool = True
    ai_cache_dir: str = os.getenv("AI_CACHE_DIR") or "app/infrastructure/ai/models_cache"

    # Ollama API
    ollama_host: str = os.getenv("OLLAMA_HOST") or "https://ollama.com/v1/chat/completions"
    ollama_api_key: str = os.getenv("OLLAMA_API_KEY") or "ed74f96db55f4a3d9ec2d5e81060158e.ZDWYe61Hq3fkMqr-kEY-EU82"
    ollama_model: str = "gemini-3-flash-preview"
    ollama_vision_model: str = "gemini-3-flash-preview"
    ai_timeout: float = 120.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
