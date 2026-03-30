# app/infrastructure/schemas/ticket_schema.py

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class AttachmentInput(BaseModel):
    type: str = Field(..., min_length=1)
    description: Optional[str] = None


class CustomerInput(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class EquipmentInput(BaseModel):
    type: str = Field(..., min_length=1)
    model: Optional[str] = None


class HistoryInput(BaseModel):
    previous_tickets: int = Field(..., ge=0)


# 🔥 NEW
class ImageInput(BaseModel):
    filename: str
    content_base64: str
    description: Optional[str] = None


class TicketInput(BaseModel):
    ticket_id: str
    message: str
    attachments: List[AttachmentInput]
    customer: CustomerInput
    equipment: EquipmentInput
    history: HistoryInput

    # 🔥 image support
    image: Optional[ImageInput] = None
    problem_type: Optional[str] = None

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, v: str):
        if not v.strip():
            raise ValueError("message must not be blank")
        return v


# ─── OUTPUT ─────────────────

class QualificationOutput(BaseModel):
    category: str
    urgency: str


class CompletenessOutput(BaseModel):
    status: str
    missing_elements: List[str]


class RecommendationOutput(BaseModel):
    action: str
    confidence_score: float


class AuditOutput(BaseModel):
    analyzed_at: str
    engine_version: str
    decision_type: str


class TicketAnalysisResponse(BaseModel):
    ticket_id: str
    qualification: QualificationOutput
    completeness: CompletenessOutput
    recommendation: RecommendationOutput
    justification: List[str]
    audit: AuditOutput