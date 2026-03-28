from datetime import datetime

from app.infrastructure.ai.vision_adapter import VisionAdapter
from app.infrastructure.ai.analysis_adapter import AIAdapter
from app.infrastructure.ai.documentation_adapter import DocumentationAdapter
from app.infrastructure.ai.documentation_ai_adapter import DocumentationAIAdapter

from app.domain.entities.ticket import TicketEntity


vision_adapter = VisionAdapter()
ai_adapter = AIAdapter()
documentation_adapter = DocumentationAdapter()
documentation_ai_adapter = DocumentationAIAdapter()


async def analyze_ticket(payload):

    product_reference = None
    documentation_message = None

    # 🔥 STEP 1: Vision → détecter référence produit
    if payload.image:
        vision_result = await vision_adapter.detect_product_reference(
            payload.image.content_base64
        )
        product_reference = vision_result.get("product_reference")

    # 🔥 STEP 2: Recherche documentation (FAISS)
    doc_chunks = []
    if product_reference and payload.equipment.type:
        doc_chunks = documentation_adapter.query(
            payload.equipment.type,
            product_reference,
            top_k=5
        )

    # 🔥 STEP 3: Génération aide technique avec LLM + documentation
    if doc_chunks:
        doc_ai_result = await documentation_ai_adapter.analyze_documentation(
            payload.equipment.type,
            product_reference,
            doc_chunks
        )
        documentation_message = doc_ai_result.get("diagnostic_help")

    # 🔥 STEP 4: Build Ticket Entity
    ticket = TicketEntity(
        ticket_id=payload.ticket_id,
        message=payload.message,
        product_reference=product_reference,
        equipment=payload.equipment.type,
        customer=payload.customer.id,
        history=payload.history.previous_tickets,
        attachments=None,
    )

    # 🔥 STEP 5: AI analysis ticket
    result = await ai_adapter.analyze_ticket(ticket)

    # 🔥 STEP 6: Message IA final utilisateur
    message_ia = None

    if doc_ai_result:
        message_ia = f"""
**Problème identifié :**

{doc_ai_result.get("diagnostic_help", "")}

**Étapes recommandées :**
"""
        for step in doc_ai_result.get("recommended_actions", []):
            message_ia += f"\n- {step}"

        if doc_ai_result.get("important_warnings"):
            message_ia += "\n\n⚠️ **Avertissements :**\n"
            for warn in doc_ai_result.get("important_warnings", []):
                message_ia += f"- {warn}\n"

    # 🔥 STEP 7: Response finale
    return {
        "ticket_id": payload.ticket_id,
        "qualification": {
            "category": result.category,
            "urgency": result.urgency,
        },
        "completeness": {
            "status": "complete",
            "missing_elements": [],
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