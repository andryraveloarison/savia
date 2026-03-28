from app.domain.entities.ticket import TicketEntity
from app.domain.types.enums import CompletenessStatus
from app.domain.rules.completeness import check_completeness


class CompletenessService:
    @staticmethod
    def run(ticket: TicketEntity) -> dict:
        """
        Vérifie la complétude d'un ticket en utilisant le moteur de règles.
        """
        attachments_raw = [
            {"type": a.type, "description": a.description} 
            for a in ticket.attachments
        ]
        
        missing = check_completeness(
            message=ticket.message,
            equipment_model=ticket.equipment.model,
            equipment_type=ticket.equipment.type,
            attachments=attachments_raw
        )

        status = CompletenessStatus.INCOMPLETE if missing else CompletenessStatus.COMPLETE
        
        return {
            "status": status,
            "missing_elements": missing
        }
