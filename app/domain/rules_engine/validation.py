"""
Règles de validation technique du ticket.
Vérifie l'intégrité de base des données.
"""

def validate_ticket_data(
    ticket_id: str,
    message: str,
    customer_id: str
) -> list[str]:
    """
    Vérifie que les données de structure du ticket sont valides.
    """
    errors = []
    
    if not ticket_id or len(ticket_id.strip()) < 3:
        errors.append("invalid_ticket_id")
        
    if not message or len(message.strip()) == 0:
        errors.append("empty_message")
        
    if not customer_id or len(customer_id.strip()) < 2:
        errors.append("invalid_customer_id")
        
    return errors
