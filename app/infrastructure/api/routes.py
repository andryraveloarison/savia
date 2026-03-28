from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
import base64

from app.application.use_cases.analyze_ticket import analyze_ticket
from app.infrastructure.schemas.ticket_schema import TicketInput

router = APIRouter()


@router.post("/tickets/analyze", tags=["Tickets"])
async def analyze_ticket_endpoint(
    ticket_id: str = Form(...),
    message: str = Form(...),
    customer_id: str = Form(...),
    customer_name: str = Form(...),
    equipment_type: str = Form(...),
    equipment_model: Optional[str] = Form(None),
    previous_tickets: int = Form(...),

    # 🔥 IMAGE upload depuis PC
    image: Optional[UploadFile] = File(None),
):
    image_base64 = None

    if image:
        content = await image.read()
        image_base64 = base64.b64encode(content).decode("utf-8")

    payload = TicketInput(
        ticket_id=ticket_id,
        message=message,
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