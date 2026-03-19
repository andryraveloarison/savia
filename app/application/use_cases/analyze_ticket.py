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
from app.infrastructure.schemas.ticket_schema import TicketInput, TicketAnalysisResponse


def execute(ticket: TicketEntity) -> dict:
    """
    Pipeline d'analyse : validation → complétude → qualification → orientation → audit.
    """
    # 1. Validation
    validation = ValidationService.run(ticket)
    if not validation["is_valid"]:
        # On peut décider de s'arrêter ici ou de continuer avec des erreurs
        pass

    # 2. Complétude (ne dépend plus de la qualification)
    completeness = CompletenessService.run(ticket)

    # 3. Qualification
    qualification = QualificationService.run(ticket)

    # 4. Orientation (anciennement recommandation)
    orientation = OrientationService.run(
        ticket,
        qualification,
        completeness
    )

    # 5. Justification
    justification = JustificationService.run(
        ticket,
        qualification,
        completeness,
        orientation
    )
    
    # 6. Audit
    audit = AuditService.run(
        orientation["action"], 
        orientation["confidence_score"]
    )

    return {
        "ticket_id": ticket.ticket_id,
        "validation": validation,
        "completeness": completeness,
        "qualification": qualification,
        "orientation": orientation,
        "justification": justification,
        "audit": audit
    }


def analyze_ticket(payload: TicketInput) -> TicketAnalysisResponse:
    """
    Orchestre la conversion Pydantic -> Entité et appelle execute().
    """
    ticket = TicketEntity(
        ticket_id=payload.ticket_id,
        message=payload.message,
        customer=CustomerEntity(id=payload.customer.id, name=payload.customer.name),
        equipment=EquipmentEntity(type=payload.equipment.type, model=payload.equipment.model),
        attachments=[AttachmentEntity(type=a.type, description=a.description) for a in payload.attachments],
        history=HistoryEntity(previous_tickets=payload.history.previous_tickets) if payload.history else None,
    )

    result = execute(ticket)

    return TicketAnalysisResponse(
        ticket_id=result["ticket_id"],
        completeness={
            "status": result["completeness"]["status"].value,
            "missing_elements": result["completeness"]["missing_elements"],
        },
        qualification={
            "category": result["qualification"]["category"].value,
            "urgency": result["qualification"]["urgency"].value,
            "is_consistent": result["qualification"]["is_consistent"],
        },
        recommendation={
            "action": result["orientation"]["action"].value,
            "confidence_score": result["orientation"]["confidence_score"],
        },
        justification=result["justification"],
        audit=result["audit"],
    )
