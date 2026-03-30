from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
import base64

from app.application.use_cases.analyze_ticket import analyze_ticket
from app.infrastructure.schemas.ticket_schema import TicketInput

router = APIRouter()


@router.post("/tickets/analyze", tags=["Tickets"])
async def analyze_ticket_endpoint(
    ticket_id: str = Form("TKT-12345", description="ID unique du ticket"),
    message: str = Form("Mon radiateur ne marche plus", description="Description du problème"),
    customer_id: str = Form("C-001", description="ID client"),
    customer_name: str = Form("Jean Dupont", description="Nom du client"),
    equipment_type: str = Form("radiateur", description="Type d'équipement (chaudière, pompe à chaleur, etc.)"),
    equipment_model: Optional[str] = Form("", description="Modèle précis (optionnel si photo fournie)"),
    previous_tickets: int = Form(0, description="Nombre de tickets précédents"),
    problem_type: Optional[str] = Form("dysfonctionnement", description="Type de problème choisi"),

    # 🔥 IMAGE upload depuis PC
    image: Optional[UploadFile] = File(None, description="Photo de la plaque signalétique"),
):
    image_base64 = None

    if image:
        content = await image.read()
        image_base64 = base64.b64encode(content).decode("utf-8")

    payload = TicketInput(
        ticket_id=ticket_id,
        message=message,
        problem_type=problem_type,
        attachments=[],
        image={
            "filename": image.filename,
            "content_base64": image_base64,
        } if image else None,
        customer={
            "id": customer_id,
            "name": customer_name,
        },
        equipment={
            "type": equipment_type,
            "model": equipment_model,
        },
        history={
            "previous_tickets": previous_tickets,
        },
    )

    return await analyze_ticket(payload)