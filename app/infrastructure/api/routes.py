"""
Routes FastAPI — endpoint POST /tickets/analyze
"""
import logging
import time
from fastapi import APIRouter
from app.infrastructure.schemas.ticket_schema import TicketInput, TicketAnalysisResponse
from app.application.use_cases.analyze_ticket import analyze_ticket
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

@router.post(
    "/tickets/analyze",
    response_model=TicketAnalysisResponse,
    status_code=200,
    summary="Analyser un ticket SAV",
    description=(
        "Reçoit un ticket SAV, vérifie sa complétude, le qualifie, "
        "propose une orientation opérationnelle et retourne une traçabilité complète."
    ),
)
async def analyze_ticket_endpoint(payload: TicketInput) -> TicketAnalysisResponse:
    """
    Endpoint principal du moteur Savia.
    """
    start_time = time.perf_counter()
    
    result = analyze_ticket(payload)
    
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    # Log structuré (correlation_id injecté par le formateur)
    logger.info(
        f"Ticket analysis completed for {payload.ticket_id}",
        extra={
            "ticket_id": payload.ticket_id,
            "engine_version": settings.engine_version,
            "action": result.recommendation.action,
            "duration_ms": round(duration_ms, 2)
        }
    )
    
    return result
