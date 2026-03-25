import logging
from typing import Optional
from app.domain.entities.ticket import TicketEntity
from app.core.exceptions import ValidationError, ConstraintViolationError
from app.shared.constants.constraints import (
    MAX_MESSAGE_SIZE_BYTES,
    MAX_ATTACHMENTS,
    AI_CALL_TIMEOUT_SECONDS,
)

logger = logging.getLogger("savia")


class ConstraintsService:
    """Service de validation des contraintes sur les tickets."""
    
    @staticmethod
    def validate_message_size(ticket: TicketEntity) -> bool:
        """
        Vérifie que la taille du message ne dépasse pas la limite.
        """
        message_size = len(ticket.message.encode('utf-8'))
        
        if message_size > MAX_MESSAGE_SIZE_BYTES:
            error_msg = (
                f"Message size ({message_size} bytes) exceeds maximum "
                f"allowed ({MAX_MESSAGE_SIZE_BYTES} bytes)"
            )
            logger.warning(f"Constraint violation - {error_msg}")
            raise ConstraintViolationError(error_msg)
        
        logger.debug(f"Message size validation passed: {message_size} bytes")
        return True
    
    @staticmethod
    def validate_attachments_count(ticket: TicketEntity) -> bool:
        """
        Vérifie que le nombre de pièces jointes ne dépasse pas la limite.
        """
        attachment_count = len(ticket.attachments)
        
        if attachment_count > MAX_ATTACHMENTS:
            error_msg = (
                f"Number of attachments ({attachment_count}) exceeds maximum "
                f"allowed ({MAX_ATTACHMENTS})"
            )
            logger.warning(f"Constraint violation - {error_msg}")
            raise ConstraintViolationError(error_msg)
        
        logger.debug(f"Attachments count validation passed: {attachment_count}")
        return True
    
    @staticmethod
    def validate_all_constraints(ticket: TicketEntity) -> dict:
        """
        Valide tous les garde-fous pour un ticket.
        """
        results = {
            "message_size_valid": False,
            "attachments_count_valid": False,
        }
        
        try:
            results["message_size_valid"] = ConstraintsService.validate_message_size(ticket)
            results["attachments_count_valid"] = ConstraintsService.validate_attachments_count(ticket)
            
            logger.info("All constraints validated successfully")
            return results
            
        except ConstraintViolationError as e:
            logger.error(f"Constraint validation failed: {str(e)}")
            raise
    
    @staticmethod
    def get_timeout_seconds() -> int:
        """Retourne le timeout en secondes pour les appels IA."""
        return AI_CALL_TIMEOUT_SECONDS
