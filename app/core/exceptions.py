import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger("savia")

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

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "validation_error", "detail": jsonable_encoder(errors)},
    )

async def global_exception_handler(request: Request, exc: Exception):
    # Conserver le comportement par défaut de Starlette pour les HTTPException (comme le 400 malformed JSON)
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
