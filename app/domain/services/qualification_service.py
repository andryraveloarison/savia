from app.domain.entities.ticket import TicketEntity
from app.domain.rules_engine.qualification import qualify_ticket


class QualificationService:
    @staticmethod
    def run(ticket: TicketEntity) -> dict:
        """
        Qualifie un ticket en utilisant le moteur de règles.
        """
        return qualify_ticket(
            message=ticket.message,
            equipment_type=ticket.equipment.type
        )
