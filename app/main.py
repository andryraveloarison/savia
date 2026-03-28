import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from scalar_fastapi import get_scalar_api_reference

from app.core.config import get_settings
from app.shared.types.version import VersionStr
from app.core.logging import setup_logging
from app.core.middleware import add_correlation_id
from app.core.exceptions import validation_exception_handler, global_exception_handler
from app.infrastructure.api.routes import router

from app.infrastructure.ai.documentation_adapter import DocumentationAdapter

# ─── Configuration ───────────────────────────────────────────────────

setup_logging()
logger = logging.getLogger("savia")
settings = get_settings()

# Variable globale pour l'app
doc_adapter: DocumentationAdapter | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} starting...")
        
    # 🔹 Initialiser DocumentationAdapter une seule fois
    global doc_adapter
    doc_adapter = DocumentationAdapter(
        docs_path="app/infrastructure/ai/docs",
        index_path="app/infrastructure/ai/faiss_index"
    )

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
