"""
Entité Ticket — représentation métier d'un ticket SAV entrant.
Indépendante de tout framework.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AttachmentEntity:
    type: str
    description: Optional[str] = None


@dataclass
class CustomerEntity:
    id: str
    name: str


@dataclass
class EquipmentEntity:
    type: str
    model: Optional[str] = None

@dataclass
class ProductReferenceEntity:
    type: str
    model: Optional[str] = None


@dataclass
class HistoryEntity:
    previous_tickets: int = 0


@dataclass
class TicketEntity:
    ticket_id: str
    message: str
    customer: CustomerEntity
    equipment: EquipmentEntity
    attachments: list[AttachmentEntity] = field(default_factory=list)
    history: Optional[HistoryEntity] = None
    product_reference: Optional[str] = None
    problem_type: Optional[str] = None
    
    @property
    def previous_tickets_count(self) -> int:
        if self.history is None:
            return 0
        return self.history.previous_tickets
