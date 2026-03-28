from app.domain.entities.ticket import TicketEntity
from app.domain.rules.validation import validate_ticket_data


class ValidationService:
    @staticmethod
    def run(ticket: TicketEntity) -> dict:
        """
        Exécute la validation technique du ticket.
        """
        errors = validate_ticket_data(
            ticket_id=ticket.ticket_id,
            message=ticket.message,
            customer_id=ticket.customer.id
        )
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
