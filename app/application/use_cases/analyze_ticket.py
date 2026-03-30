from datetime import datetime
from dataclasses import replace

from app.infrastructure.ai.vision_adapter import VisionAdapter
from app.infrastructure.ai.analysis_adapter import AIAdapter
from app.infrastructure.ai.documentation_adapter import DocumentationAdapter
from app.infrastructure.ai.documentation_ai_adapter import DocumentationAIAdapter

from app.domain.entities.ticket import TicketEntity


from app.infrastructure.ai.registry import ai_registry
from app.domain.entities.ticket import TicketEntity


async def analyze_ticket(payload):

    product_reference = payload.equipment.model
    documentation_message = None
    doc_ai_result = None

    # STEP 1: Vision → détecter référence produit (si pas fournie)
    if not product_reference and payload.image:
        vision_result = await ai_registry.vision.detect_product_reference(
            payload.image.content_base64
        )
        product_reference = vision_result.get("product_reference")

    # STEP 2: Recherche documentation (FAISS)
    doc_chunks = []
    if product_reference and payload.equipment.type:
        doc_chunks = ai_registry.documentation.query(
            payload.equipment.type,
            product_reference,
            user_message=payload.message,
            top_k=5
        )

    # STEP 3: Génération aide technique avec LLM + documentation
    if doc_chunks:
        doc_ai_result = await ai_registry.documentation_ai.analyze_documentation(
            payload.equipment.type,
            product_reference,
            doc_chunks,
            user_message=payload.message
        )
        documentation_message = doc_ai_result.get("diagnostic_help")

    # STEP 4: Build Ticket Entity
    ticket = TicketEntity(
        ticket_id=payload.ticket_id,
        message=payload.message,
        product_reference=product_reference,
        equipment=payload.equipment.type,
        customer=payload.customer.id,
        history=payload.history.previous_tickets,
        attachments=None,
        problem_type=payload.problem_type,
    )

    # STEP 6: AI analysis ticket
    result = await ai_registry.ai.analyze_ticket(ticket, has_documentation=bool(doc_chunks))

    # STEP 7: Message IA final utilisateur
    # 🔹 Priorité à la documentation si disponible et pertinente
    message_ia = None
    
    # Si on a un résultat doc avec une confiance décente (> 0.7) et des actions concrètes
    if doc_ai_result and doc_ai_result.get("confidence_score", 0) >= 0.7 and doc_ai_result.get("recommended_actions"):
        # On override l'action si c'était plus restrictif
        if result.action in ["request_additional_info", "escalate_to_human"]:
             result = replace(
                 result,
                 action="auto_resolution",
                 confidence_score=doc_ai_result["confidence_score"],
                 justifications=["Solution trouvée dans la documentation technique."]
             )

        message_ia = f"""
**Problème identifié :** {doc_ai_result.get("diagnostic_help", "")}

**Étapes recommandées :**
"""
        for step in doc_ai_result.get("recommended_actions", []):
            message_ia += f"\n- {step}"

        if doc_ai_result.get("important_warnings"):
            message_ia += "\n\n⚠️ **Avertissements :**\n"
            for warn in doc_ai_result.get("important_warnings", []):
                message_ia += f"- {warn}\n"
    
    # Si pas de doc ou doc peu fiable, on prend le message de l'agent de classification
    if not message_ia:
        message_ia = result.message_ia
        
        # Sécurité anti-hallucination : 
        # Si on a cherché dans la doc (chunks trouvés) mais que la confiance est nulle/basse,
        # et que l'expert classification pensait avoir trouvé une solution ou voulait escalader,
        # on doit forcer l'escalade car le classifier ne peut pas "deviner" la solution si la doc ne l'a pas.
        # MAIS : on ne doit pas écraser une demande d'info (vague) ou une intervention déjà décidée.
        if doc_chunks and (not doc_ai_result or doc_ai_result.get("confidence_score", 0) < 0.7):
            if result.action not in ["request_additional_info", "schedule_intervention"]:
                result = replace(
                    result,
                    action="escalate_to_human",
                    justifications=["Problème non résolu via documentation (confiance basse ou inexistant)."]
                )
                message_ia = "Nous avons consulté la documentation technique mais n'avons pas trouvé de solution précise pour ce problème. Un technicien va vous recontacter."

    # STEP 8: Response finale (Qualification / Completeness enrichies par result)
    return {
        "ticket_id": payload.ticket_id,
        "qualification": {
            "category": result.category,
            "urgency": result.urgency,
        },
        "completeness": {
            "status": "incomplete" if result.action == "request_additional_info" else "complete",
            "missing_elements": result.justifications if result.action == "request_additional_info" else [],
        },
        "recommendation": {
            "action": result.action,
            "confidence_score": result.confidence_score,
        },
        "justification": result.justifications,
        "audit": {
            "analyzed_at": datetime.utcnow().isoformat(),
            "engine_version": "v3-rag-multi-agent",
            "decision_type": "AI",
        },
        "product_reference": product_reference,
        "messageIA": message_ia,
    }