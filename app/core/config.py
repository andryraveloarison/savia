"""
Configuration globale de l'application Savia.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from app.shared.types.version import VersionStr

class Settings(BaseSettings):
    app_name: str = "Savia — Moteur d'aide à la décision SAV"
    app_version: VersionStr = "1.1.0"
    debug: bool = False
    engine_version: VersionStr = "savia-mvp-v1"
    confidence_threshold_escalate: float = 0.40
    confidence_threshold_ai: float = 0.5
    
    ai_enabled: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
