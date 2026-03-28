from app.domain.entities.ticket import TicketEntity
from app.domain.rules.scoring import compute_confidence_score
from app.domain.rules.orientation import decide_action


class OrientationService:
    @staticmethod
    def run(ticket: TicketEntity, qualification: dict, completeness: dict) -> dict:
        """
        Génère une orientation en utilisant le moteur de règles.
        """
        missing_elements = completeness["missing_elements"]
        
        # Le calcul du score de confiance est maintenant centralisé
        attachments_raw = [
            {"type": a.type, "description": a.description} 
            for a in ticket.attachments
        ]
        from app.domain.rules.completeness import has_exploitable_attachment
        has_attachment = has_exploitable_attachment(attachments_raw)

        confidence = compute_confidence_score(
            keyword_match_ratio=qualification["keyword_match_ratio"],
            equipment_type=ticket.equipment.type,
            previous_tickets=ticket.previous_tickets_count,
            missing_elements=missing_elements,
            has_useful_attachment=has_attachment,
        )

        action = decide_action(
            message=ticket.message,
            urgency=qualification["urgency"],
            equipment_type=ticket.equipment.type,
            previous_tickets_count=ticket.previous_tickets_count,
            confidence_score=confidence,
            missing_elements=missing_elements
        )

        return {
            "action": action,
            "confidence_score": confidence
        }
