import time
from app.core.config import get_settings
from app.core.logging import log_ticket_analysis
from app.shared.types.common import DurationMs
from app.domain.entities.ticket import (
    TicketEntity, AttachmentEntity, CustomerEntity,
    EquipmentEntity, HistoryEntity,
)
from app.domain.services.validation_service import ValidationService
from app.domain.services.completeness_service import CompletenessService
from app.domain.services.qualification_service import QualificationService
from app.domain.services.orientation_service import OrientationService
from app.domain.services.justification_service import JustificationService
from app.domain.services.audit_service import AuditService
from app.domain.services.ai_analysis_service import AIAnalysisService

from app.infrastructure.ai.mock_client import MockAIClient
from app.infrastructure.ai.ollama_client import OllamaClient
from app.infrastructure.schemas.ticket_schema import TicketInput, TicketAnalysisResponse

settings = get_settings()

def get_ai_client():
    if settings.ai_provider == "ollama":
        return OllamaClient(base_url=settings.ollama_url)
    return MockAIClient()

async def execute(ticket: TicketEntity) -> dict:
    """
    Pipeline d'analyse : validation → complétude → [IA ou Règles] → justification → audit.
    """
    # 1. Validation
    validation = ValidationService.run(ticket)

    # 2. Complétude
    completeness = CompletenessService.run(ticket)

    # 3 & 4. Qualification & Orientation (via AI ou Rules avec AIAnalysisService)
    ai_client = get_ai_client()
    analysis = await AIAnalysisService.run(ticket, ai_client, completeness)

    # 5. Justification
    # Note: On adapte justification pour prendre les infos de l'analyse (IA ou Rules)
    justification = JustificationService.run(
        ticket,
        {
            "category": analysis["category"],
            "urgency": analysis["urgency"],
            "is_consistent": True # Simplification pour l'IA
        },
        completeness,
        {
            "action": analysis["action"],
            "confidence_score": analysis["confidence_score"]
        }
    )
    
    # On ajoute au besoin les justifications spécifiques de l'IA
    justification.extend(analysis.get("justifications", []))
    
    # 6. Audit
    audit = AuditService.run(
        analysis["action"], 
        analysis["confidence_score"]
    )
    audit["provider"] = analysis.get("provider", "unknown")

    return {
        "ticket_id": ticket.ticket_id,
        "validation": validation,
        "completeness": completeness,
        "qualification": {
            "category": analysis["category"],
            "urgency": analysis["urgency"],
            "is_consistent": True
        },
        "orientation": {
            "action": analysis["action"],
            "confidence_score": analysis["confidence_score"]
        },
        "justification": justification,
        "audit": audit
    }


async def analyze_ticket(payload: TicketInput) -> TicketAnalysisResponse:
    """
    Orchestre l'analyse asynchrone pour supporter les appels LLM.
    """
    start_time = time.perf_counter()
    
    ticket = TicketEntity(
        ticket_id=payload.ticket_id,
        message=payload.message,
        customer=CustomerEntity(id=payload.customer.id, name=payload.customer.name),
        equipment=EquipmentEntity(type=payload.equipment.type, model=payload.equipment.model),
        attachments=[AttachmentEntity(type=a.type, description=a.description) for a in payload.attachments],
        history=HistoryEntity(previous_tickets=payload.history.previous_tickets) if payload.history else None,
    )

    result_dict = await execute(ticket)

    response = TicketAnalysisResponse(
        ticket_id=result_dict["ticket_id"],
        completeness={
            "status": result_dict["completeness"]["status"].value,
            "missing_elements": result_dict["completeness"]["missing_elements"],
        },
        qualification={
            "category": result_dict["qualification"]["category"].value,
            "urgency": result_dict["qualification"]["urgency"].value,
            "is_consistent": result_dict["qualification"]["is_consistent"],
        },
        recommendation={
            "action": result_dict["orientation"]["action"].value,
            "confidence_score": result_dict["orientation"]["confidence_score"],
        },
        justification=result_dict["justification"],
        audit=result_dict["audit"],
    )

    duration_ms: DurationMs = (time.perf_counter() - start_time) * 1000
    
    log_ticket_analysis(
        payload_ticket_id=payload.ticket_id,
        engine_version=settings.engine_version,
        action=response.recommendation.action,
        duration_ms=duration_ms
    )

    return response
