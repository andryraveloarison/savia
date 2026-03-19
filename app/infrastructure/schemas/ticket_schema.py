"""
Schemas Pydantic — validation stricte des entrées/sorties de l'API.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# ─── Input Schemas ────────────────────────────────────────────────────

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


class TicketInput(BaseModel):
    ticket_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    attachments: List[AttachmentInput] = Field(default_factory=list)
    customer: CustomerInput
    equipment: EquipmentInput
    history: Optional[HistoryInput] = None

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message must not be blank")
        return v


# ─── Output Schemas ───────────────────────────────────────────────────

class ValidationOutput(BaseModel):
    is_valid: bool
    errors: List[str]


class QualificationOutput(BaseModel):
    category: str
    urgency: str
    is_consistent: bool


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
