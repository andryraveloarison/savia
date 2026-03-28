import pytest
from app.domain.rules.validation import validate_ticket_data

def test_validate_ticket_data_success():
    errors = validate_ticket_data("SAV-001", "Mon chauffage est en panne", "C-123")
    assert len(errors) == 0

def test_validate_ticket_data_invalid_id():
    # Ticket ID trop court
    errors = validate_ticket_data("S1", "Message valid", "C-123")
    assert "invalid_ticket_id" in errors
    
    # Ticket ID vide ou espaces
    errors = validate_ticket_data("  ", "Message valid", "C-123")
    assert "invalid_ticket_id" in errors

def test_validate_ticket_data_empty_message():
    # Message vide
    errors = validate_ticket_data("SAV-001", "", "C-123")
    assert "empty_message" in errors
    
    # Message avec uniquement des espaces
    errors = validate_ticket_data("SAV-001", "   ", "C-123")
    assert "empty_message" in errors

def test_validate_ticket_data_invalid_customer():
    # Customer ID trop court
    errors = validate_ticket_data("SAV-001", "Message valid", "C")
    assert "invalid_customer_id" in errors
    
    # Customer ID vide
    errors = validate_ticket_data("SAV-001", "Message valid", " ")
    assert "invalid_customer_id" in errors

def test_validate_ticket_data_multiple_errors():
    errors = validate_ticket_data("", " ", "")
    assert "invalid_ticket_id" in errors
    assert "empty_message" in errors
    assert "invalid_customer_id" in errors
