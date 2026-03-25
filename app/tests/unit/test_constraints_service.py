"""
Tests pour le ConstraintsService - Validation des garde-fous.
"""
import pytest
import asyncio
from app.domain.entities.ticket import TicketEntity, CustomerEntity, EquipmentEntity, AttachmentEntity
from app.domain.services.constraints_service import ConstraintsService, ConstraintViolationError
from app.shared.constants.constraints import (
    MAX_MESSAGE_SIZE_BYTES,
    MAX_ATTACHMENTS,
    AI_CALL_TIMEOUT_SECONDS,
)


class TestConstraintsService:
    """Test suite pour ConstraintsService."""
    
    @pytest.fixture
    def valid_ticket(self) -> TicketEntity:
        """Crée un ticket valide (respecte tous les garde-fous)."""
        return TicketEntity(
            ticket_id="TICKET-001",
            message="Ma machine ne fonctionne pas.",
            customer=CustomerEntity(id="CUST-001", name="John Doe"),
            equipment=EquipmentEntity(type="laptop", model="Dell XPS 13"),
            attachments=[
                AttachmentEntity(type="image", description="Screenshot of error"),
            ],
        )
    
    @pytest.fixture
    def oversized_message_ticket(self) -> TicketEntity:
        """Crée un ticket avec un message dépassant la limite."""
        return TicketEntity(
            ticket_id="TICKET-002",
            message="x" * (MAX_MESSAGE_SIZE_BYTES + 1),
            customer=CustomerEntity(id="CUST-002", name="Jane Doe"),
            equipment=EquipmentEntity(type="desktop", model="HP Desktop"),
            attachments=[],
        )
    
    @pytest.fixture
    def too_many_attachments_ticket(self) -> TicketEntity:
        """Crée un ticket avec trop de pièces jointes."""
        attachments = [
            AttachmentEntity(type="image", description=f"Attachment {i}")
            for i in range(MAX_ATTACHMENTS + 1)
        ]
        return TicketEntity(
            ticket_id="TICKET-003",
            message="Help needed urgently!",
            customer=CustomerEntity(id="CUST-003", name="Alice Smith"),
            equipment=EquipmentEntity(type="printer", model="Brother HL-L8360CDW"),
            attachments=attachments,
        )
    
    # ─── Message Size Tests ─────────────────────────────────────────────────────
    
    def test_message_size_validation_passes_for_valid_size(self, valid_ticket):
        """Vérifie que la validation passe pour un message de taille valide."""
        result = ConstraintsService.validate_message_size(valid_ticket)
        assert result is True
    
    def test_message_size_validation_fails_for_oversized_message(self, oversized_message_ticket):
        """Vérifie que la validation échoue pour un message trop volumineux."""
        with pytest.raises(ConstraintViolationError) as exc_info:
            ConstraintsService.validate_message_size(oversized_message_ticket)
        
        assert "Message size" in str(exc_info.value)
        assert "exceeds maximum" in str(exc_info.value)
    
    def test_message_size_validation_boundary_condition_at_limit(self):
        """Teste le cas limite exactement à la limite de taille."""
        # Crée un message exactement à la limite
        exact_size_message = "x" * MAX_MESSAGE_SIZE_BYTES
        ticket = TicketEntity(
            ticket_id="TICKET-004",
            message=exact_size_message,
            customer=CustomerEntity(id="CUST-004", name="Bob"),
            equipment=EquipmentEntity(type="monitor"),
            attachments=[],
        )
        
        result = ConstraintsService.validate_message_size(ticket)
        assert result is True
    
    
    # ─── Attachments Count Tests ───────────────────────────────────────────────
    
    def test_attachments_count_validation_passes_for_valid_count(self, valid_ticket):
        """Vérifie que la validation passe pour un nombre valide de pièces jointes."""
        result = ConstraintsService.validate_attachments_count(valid_ticket)
        assert result is True
    
    def test_attachments_count_validation_passes_for_no_attachments(self):
        """Vérifie que la validation passe quand il n'y a aucune pièce jointe."""
        ticket = TicketEntity(
            ticket_id="TICKET-006",
            message="No attachments here.",
            customer=CustomerEntity(id="CUST-006", name="Diana"),
            equipment=EquipmentEntity(type="tablet"),
            attachments=[],
        )
        
        result = ConstraintsService.validate_attachments_count(ticket)
        assert result is True
    
    def test_attachments_count_validation_fails_for_too_many(self, too_many_attachments_ticket):
        """Vérifie que la validation échoue pour trop de pièces jointes."""
        with pytest.raises(ConstraintViolationError) as exc_info:
            ConstraintsService.validate_attachments_count(too_many_attachments_ticket)
        
        assert "Number of attachments" in str(exc_info.value)
        assert "exceeds maximum" in str(exc_info.value)
    
    def test_attachments_count_validation_boundary_condition_at_limit(self):
        """Teste le cas limite exactement au nombre maximum de pièces jointes."""
        attachments = [
            AttachmentEntity(type="image", description=f"Attachment {i}")
            for i in range(MAX_ATTACHMENTS)
        ]
        ticket = TicketEntity(
            ticket_id="TICKET-007",
            message="With maximum attachments",
            customer=CustomerEntity(id="CUST-007", name="Eve"),
            equipment=EquipmentEntity(type="camera"),
            attachments=attachments,
        )
        
        result = ConstraintsService.validate_attachments_count(ticket)
        assert result is True
    
    # ─── All Constraints Tests ────────────────────────────────────────────────
    
    def test_validate_all_constraints_passes_for_valid_ticket(self, valid_ticket):
        """Vérifie que tous les garde-fous passent pour un ticket valide."""
        result = ConstraintsService.validate_all_constraints(valid_ticket)
        
        assert result["message_size_valid"] is True
        assert result["attachments_count_valid"] is True
    
    def test_validate_all_constraints_fails_on_first_violation(self, oversized_message_ticket):
        """Vérifie que la validation globale échoue quand une contrainte est violée."""
        with pytest.raises(ConstraintViolationError):
            ConstraintsService.validate_all_constraints(oversized_message_ticket)
    
    def test_validate_all_constraints_fails_on_message_size_violation(self):
        """Vérifie que la validation échoue pour une violation de taille de message."""
        ticket = TicketEntity(
            ticket_id="TICKET-008",
            message="x" * (MAX_MESSAGE_SIZE_BYTES + 1),
            customer=CustomerEntity(id="CUST-008", name="Frank"),
            equipment=EquipmentEntity(type="server"),
            attachments=[],
        )
        
        with pytest.raises(ConstraintViolationError) as exc_info:
            ConstraintsService.validate_all_constraints(ticket)
        
        assert "Message size" in str(exc_info.value)
    
    def test_validate_all_constraints_fails_on_attachments_violation(self, too_many_attachments_ticket):
        """Vérifie que la validation échoue pour une violation du nombre de pièces jointes."""
        with pytest.raises(ConstraintViolationError) as exc_info:
            ConstraintsService.validate_all_constraints(too_many_attachments_ticket)
        
        assert "Number of attachments" in str(exc_info.value)
    
    # ─── Timeout Tests ──────────────────────────────────────────────────────────
    
    def test_get_timeout_seconds_returns_positive_value(self):
        """Vérifie que le timeout retourné est positif."""
        timeout = ConstraintsService.get_timeout_seconds()
        assert isinstance(timeout, int)
        assert timeout > 0
    
    def test_get_timeout_seconds_returns_reasonable_value(self):
        """Vérifie que le timeout est raisonnable (entre 5 et 120 secondes)."""
        timeout = ConstraintsService.get_timeout_seconds()
        assert 5 <= timeout <= 120
    
    def test_timeout_configuration_value(self):
        """Vérifie la valeur configurée du timeout."""
        assert AI_CALL_TIMEOUT_SECONDS == 30
    
    # ─── Multiple Violations Tests ──────────────────────────────────────────────
    
    def test_ticket_violating_multiple_constraints(self):
        """Crée un ticket violant à la fois la taille de message et le nombre de pièces jointes."""
        attachments = [
            AttachmentEntity(type="image", description=f"Attachment {i}")
            for i in range(MAX_ATTACHMENTS + 1)
        ]
        ticket = TicketEntity(
            ticket_id="TICKET-009",
            message="x" * (MAX_MESSAGE_SIZE_BYTES + 1),
            customer=CustomerEntity(id="CUST-009", name="Grace"),
            equipment=EquipmentEntity(type="network"),
            attachments=attachments,
        )
        
        # La validation devrait échouer sur le premier check
        with pytest.raises(ConstraintViolationError):
            ConstraintsService.validate_all_constraints(ticket)
    
    # ─── Error Message Tests ────────────────────────────────────────────────────
    
    def test_error_message_includes_size_information(self):
        """Vérifie que les messages d'erreur incluent les informations de taille."""
        oversized_message = "x" * (MAX_MESSAGE_SIZE_BYTES + 100)
        ticket = TicketEntity(
            ticket_id="TICKET-010",
            message=oversized_message,
            customer=CustomerEntity(id="CUST-010", name="Henry"),
            equipment=EquipmentEntity(type="audio"),
            attachments=[],
        )
        
        with pytest.raises(ConstraintViolationError) as exc_info:
            ConstraintsService.validate_message_size(ticket)
        
        error_message = str(exc_info.value)
        assert "bytes" in error_message
        assert str(len(oversized_message.encode('utf-8'))) in error_message
        assert str(MAX_MESSAGE_SIZE_BYTES) in error_message
    
    def test_error_message_includes_attachment_count_information(self):
        """Vérifie que les messages d'erreur incluent le nombre de pièces jointes."""
        attachments = [
            AttachmentEntity(type="image", description=f"Attachment {i}")
            for i in range(MAX_ATTACHMENTS + 3)
        ]
        ticket = TicketEntity(
            ticket_id="TICKET-011",
            message="Error message test",
            customer=CustomerEntity(id="CUST-011", name="Iris"),
            equipment=EquipmentEntity(type="mobile"),
            attachments=attachments,
        )
        
        with pytest.raises(ConstraintViolationError) as exc_info:
            ConstraintsService.validate_attachments_count(ticket)
        
        error_message = str(exc_info.value)
        assert str(len(attachments)) in error_message
        assert str(MAX_ATTACHMENTS) in error_message

