DEFAULT_CUSTOMER_NAME = "John Doe"

TICKET_ANALYZE_EXAMPLES = {
    "T1_heating": {
        "summary": "T1 - Chauffage",
        "description": "Problème de chauffage (Chaudière)",
        "value": {
            "ticket_id": "REQ-T1",
            "attachments": [],
            "message": "Chauffage ne démarre plus ce matin",
            "customer": {"id": "C-123", "name": DEFAULT_CUSTOMER_NAME},
            "equipment": {"type": "boiler", "model": None},
            "history": {"previous_tickets": 0}
        },
    },
    "T2_plumbing": {
        "summary": "T2 - Plomberie",
        "description": "Fuite d'eau (Robinet)",
        "value": {
            "ticket_id": "REQ-T2",
            "attachments": [],
            "message": "Fuite d'eau sous l'évier, inondation en cours",
            "customer": {"id": "C-123", "name": DEFAULT_CUSTOMER_NAME},
            "equipment": {"type": "faucet", "model": None},
            "history": {"previous_tickets": 0}
        },
    },
    "T3_electrical": {
        "summary": "T3 - Électricité",
        "description": "Disjoncteur qui saute",
        "value": {
            "ticket_id": "REQ-T3",
            "attachments": [],
            "message": "Disjoncteur qui saute régulièrement",
            "customer": {"id": "C-123", "name": DEFAULT_CUSTOMER_NAME},
            "equipment": {"type": "circuit_breaker", "model": "ABB-123"},
            "history": {"previous_tickets": 0}
        },
    },
    "T4_other": {
        "summary": "T4 - Inconnu/Autre",
        "description": "Message vague ou équipement inconnu",
        "value": {
            "ticket_id": "REQ-T4",
            "attachments": [],
            "message": "Problème",
            "customer": {"id": "C-123", "name": DEFAULT_CUSTOMER_NAME},
            "equipment": {"type": "unknown", "model": None},
            "history": {"previous_tickets": 0}
        },
    },
    "T5_heating_urgent": {
        "summary": "T5 - Chauffage Urgent",
        "description": "Panne chaudière gaz",
        "value": {
            "ticket_id": "REQ-T5",
            "attachments": [],
            "message": "Chaudière gaz en panne, 1er ticket client",
            "customer": {"id": "C-123", "name": DEFAULT_CUSTOMER_NAME},
            "equipment": {"type": "boiler", "model": None},
            "history": {"previous_tickets": 0}
        },
    }
}
