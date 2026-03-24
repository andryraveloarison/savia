from app.domain.entities.ticket import TicketEntity
from app.domain.types.enums import Category, Urgency, Action, CompletenessStatus
from app.core.config import get_settings
from app.shared.constants.equipment import EQUIPMENT_CATEGORY_MAP

settings = get_settings()

class JustificationService:
    @staticmethod
    def run(ticket: TicketEntity, qualification: dict, completeness: dict, orientation: dict) -> list[str]:
        category = qualification["category"]
        urgency = qualification["urgency"]
        completeness_status = completeness["status"]
        missing_elements = completeness["missing_elements"]
        action = orientation["action"]
        confidence_score = orientation["confidence_score"]

        justifications: list[str] = [
            f"{category.value.capitalize()} issue detected based on message content and equipment type"
        ]

        equipment_type = (ticket.equipment.type or "").lower()
        if equipment_type in EQUIPMENT_CATEGORY_MAP:
            justifications.append(f"Equipment type '{equipment_type}' matched known category '{category.value}'")

        urgency_justifications = {
            Urgency.HIGH: "High urgency keywords detected in message",
            Urgency.CRITICAL: "Critical urgency indicators detected — immediate action required",
            Urgency.MEDIUM: "Medium urgency detected — equipment is non-functional",
            Urgency.LOW: "No urgency keywords detected — low priority issue",
        }
        justifications.append(urgency_justifications[urgency])

        if completeness_status == CompletenessStatus.COMPLETE:
            justifications.append("All required information is present in the ticket")
        else:
            justifications.extend(JustificationService._get_missing_info_justifications(missing_elements))

        count = ticket.previous_tickets_count
        if count == 0:
            justifications.append("First ticket for this customer — no historical data available")
        else:
            justifications.append(f"Customer has {count} previous ticket(s)")

        if confidence_score < settings.confidence_threshold_escalate:
            justifications.append(f"Confidence score {confidence_score} is below threshold — escalated to human")
        else:
            action_reasons = {
                Action.AUTO_RESOLUTION: "Low urgency, known equipment, no missing data — auto-resolution applicable",
                Action.REQUEST_ADDITIONAL_INFO: "Missing elements prevent accurate diagnosis",
                Action.SCHEDULE_INTERVENTION: "Technical intervention required based on urgency and available info",
                Action.GENERATE_QUOTE: "Replacement or installation detected — quote needed before proceeding",
                Action.ESCALATE_TO_HUMAN: "Ambiguous case — human review required",
            }
            justifications.append(action_reasons.get(action, "Decision based on combined criteria"))
        
        return justifications

    @staticmethod
    def _get_missing_info_justifications(missing_elements: list[str]) -> list[str]:
        """Helper to get justifications for missing elements."""
        missing_justifications = []
        for elem in missing_elements:
            if elem == "equipment_model":
                missing_justifications.append("Equipment model is missing — cannot identify specific part")
            elif elem == "clear_photo":
                missing_justifications.append("No exploitable photo provided — visual diagnosis impossible")
            elif elem == "detailed_message":
                missing_justifications.append("Message is too short — insufficient problem description")
            elif elem.startswith("category_mismatch"):
                missing_justifications.append(f"Inconsistency detected: {elem.replace(':', ': ').replace(',', ', ')}")
        return missing_justifications
