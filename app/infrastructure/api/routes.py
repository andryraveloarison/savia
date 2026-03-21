from fastapi import APIRouter, Body
from app.infrastructure.schemas.ticket_schema import TicketInput, TicketAnalysisResponse
from app.application.use_cases.analyze_ticket import analyze_ticket
from app.infrastructure.schemas.examples import TICKET_ANALYZE_EXAMPLES

router = APIRouter()

@router.post("/tickets/analyze", tags=["Tickets"], response_model=TicketAnalysisResponse)
async def analyze_ticket_endpoint(
    payload: TicketInput = Body(..., openapi_examples=TICKET_ANALYZE_EXAMPLES)
) -> TicketAnalysisResponse:
    """
    Analyse un message client pour qualifier le besoin SAV et recommander une action.
    """
    return await analyze_ticket(payload)
