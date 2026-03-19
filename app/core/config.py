"""
Configuration globale de l'application Savia.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
 

class Settings(BaseSettings):
    app_name: str = "Savia — Moteur d'aide à la décision SAV"
    app_version: str = "1.0.0"
    debug: bool = False
    engine_version: str = "savia-mvp-v1"
    confidence_threshold_escalate: float = 0.40
    confidence_threshold_auto: float = 0.85

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
