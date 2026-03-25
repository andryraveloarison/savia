import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger("savia")


# ─── Custom Exceptions ───────────────────────────────────────────────────────

class ValidationError(Exception):
    """Exception levée lors de la validation d'une entité."""
    pass


class ConstraintViolationError(ValidationError):
    """Exception levée quand une contrainte (garde-fou) est violée."""
    pass


# ─── Exception Handlers ──────────────────────────────────────────────────────

def validation_exception_handler(_request: Request, exc: RequestValidationError):
    # Log details for easier debugging
    logger.warning("Validation error", extra={"detail": exc.errors()})
    
    errors = exc.errors()
    
    # Types d'erreurs considérés comme "Structurels / Mal formés" -> 400
    # - missing: champ obligatoire manquant
    # - json_invalid: JSON syntaxiquement incorrect
    # - type_error: type invalide (ex: int au lieu de string)
    structural_error_types = {"missing", "json_invalid"}
    
    is_structural = any(
        err.get("type") in structural_error_types or 
        (err.get("type") and "type_error" in err.get("type")) 
        for err in errors
    )

    if is_structural:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "malformed_json", "detail": jsonable_encoder(errors)},
        )

    # Par défaut, si c'est une erreur de "contenu" (ex: message vide, trop court) -> 422
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"error": "inexploitable_ticket", "detail": jsonable_encoder(errors)},
    )

def global_exception_handler(request: Request, exc: Exception):
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
