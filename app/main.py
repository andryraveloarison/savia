import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from app.core.config import get_settings
from app.shared.types.version import VersionStr
from app.core.logging import setup_logging
from app.core.middleware import add_correlation_id
from app.core.exceptions import validation_exception_handler, global_exception_handler
from app.infrastructure.api.routes import router

from app.infrastructure.ai.registry import ai_registry

# ─── Configuration ───────────────────────────────────────────────────

setup_logging()
logger = logging.getLogger("savia")
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} starting...")
        
    # 🔹 Pré-charger les adaptateurs via le registre (Singleton)
    # Cela déclenche le chargement des modèles et des indexes
    _ = ai_registry.documentation
    logger.info("✅ Registre IA prêt (modèles et documentation chargés)")

    yield
    logger.info("👋 Savia shutting down.")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Moteur d'aide à la décision SAV pour installateurs.",
    lifespan=lifespan,
    docs_url=None, 
    redoc_url=None
)

# ─── Middleware ──────────────────────────────────────────────────────

app.middleware("http")(add_correlation_id)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ──────────────────────────────────────────────────────────

app.include_router(router)

@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )

# ─── Exception Handlers ──────────────────────────────────────────────

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "engine": settings.engine_version, "version": settings.app_version}
