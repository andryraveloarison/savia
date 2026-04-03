from datetime import datetime
from app.domain.entities.ticket import TicketEntity
from app.infrastructure.ai.registry import ai_registry
from app.core.config import get_settings


async def analyze_ticket(payload):
    settings = get_settings()

    product_reference = payload.equipment.model
    
    # --- LLM CALL 1: VISION (SI BESOIN) ---
    if not product_reference and payload.image:
        vision_result = await ai_registry.vision_agent.process(
            payload.image.content_base64
        )
        product_reference = vision_result.get("product_reference")

    # --- RECHERCHE DOCUMENTAIRE (LOCAL / FAISS) ---
    doc_chunks = []
    if product_reference and payload.equipment.type:
        doc_chunks = await ai_registry.searcher_agent.process(
            category=payload.equipment.type,
            product_ref=product_reference,
            user_message=payload.message,
            top_k=5
        )

    # Build Ticket Entity for the agent
    ticket_entity = TicketEntity(
        ticket_id=payload.ticket_id,
        message=payload.message,
        product_reference=product_reference,
        equipment=payload.equipment.type,
        customer=payload.customer.id,
        history=payload.history.previous_tickets,
        attachments=None,
        problem_type=payload.problem_type,
    )

    # --- LLM CALL 2: ANALYSE UNIFIÉE (DIAGNOSTIC + CLASSIFICATION) ---
    result = await ai_registry.analyser_agent.process(
        ticket=ticket_entity,
        doc_chunks=doc_chunks
    )

    # --- RÈGLE MÉTIER : SEUIL DE CONFIANCE ---
    action = result.get("action", "escalate_to_human")
    confidence_score = result.get("confidence_score", 0.0)
    message_ia = result.get("message_ia")
    justifications = result.get("justifications", [])

    if action == "auto_resolution" and confidence_score < settings.confidence_threshold_escalate:
        action = "escalate_to_human"
        justifications.append(f"Score de confiance ({confidence_score}) insuffisant pour une résolution automatique.")
        message_ia = "Nous avons consulté la documentation technique mais n'avons pas trouvé de solution précise pour ce problème. Un technicien va vous recontacter."

    # STEP 8: Response finale formattée
    return {
        "ticket_id": payload.ticket_id,
        "qualification": {
            "category": result.get("category", "other"),
            "urgency": result.get("urgency", "low"),
        },
        "completeness": {
            "status": "incomplete" if action == "request_additional_info" else "complete",
            "missing_elements": justifications if action == "request_additional_info" else [],
        },
        "recommendation": {
            "action": action,
            "confidence_score": confidence_score,
        },
        "justification": justifications,
        "audit": {
            "analyzed_at": datetime.utcnow().isoformat(),
            "engine_version": "v5-unified-2-llm",
            "decision_type": "AI",
        },
        "product_reference": product_reference,
        "messageIA": message_ia,
        "diagnostic_help": result.get("diagnostic_help"),
    }