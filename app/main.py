import logging
import uuid
import time
from contextlib import asynccontextmanager
from contextvars import ContextVar

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pythonjsonlogger import jsonlogger
from scalar_fastapi import get_scalar_api_reference

from app.core.config import get_settings
from app.infrastructure.api.routes import router

# ─── Configuration du Logging Structuré ───────────────────────────────

correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="n/a")

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record["correlation_id"] = correlation_id_ctx.get()
        if not log_record.get("timestamp"):
            log_record["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if log_record.get("levelname"):
            log_record["level"] = log_record["levelname"].upper()
        else:
            log_record["level"] = record.levelname

logHandler = logging.StreamHandler()
formatter = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
logHandler.setFormatter(formatter)

# Reset les handlers par défaut pour ne pas avoir de doublons
root_logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)
root_logger.addHandler(logHandler)
root_logger.setLevel(logging.INFO)

logger = logging.getLogger("savia")

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} starting...")
    yield
    logger.info("👋 Savia shutting down.")

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Moteur d'aide à la décision SAV pour installateurs.",
    lifespan=lifespan,
    docs_url=None, 
    redoc_url=None
)

# ─── Middleware de Correlation ID ──────────────────────────────────────

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    token = correlation_id_ctx.set(correlation_id)
    try:
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
    finally:
        correlation_id_ctx.reset(token)

app.include_router(router)

@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log details for easier debugging
    logger.warning("Validation error", extra={"detail": exc.errors()})
    
    # Si l'erreur est syntaxique (JSON malformé), on renvoie 400
    errors = exc.errors()
    if any(err.get("type") == "json_invalid" for err in errors):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "malformed_json", "detail": "Invalid JSON syntax"},
        )

    from fastapi.encoders import jsonable_encoder
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "validation_error", "detail": jsonable_encoder(errors)},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Conserver le comportement par défaut de Starlette pour les HTTPException (comme le 400 malformed JSON)
    from fastapi.exceptions import HTTPException
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "http_error", "detail": exc.detail},
        )
    
    logger.exception(f"Unhandled error on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "internal_server_error", "detail": "An unexpected error occurred."},
    )

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "engine": settings.engine_version, "version": settings.app_version}
