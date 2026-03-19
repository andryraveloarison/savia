from enum import Enum


class Category(str, Enum):
    HEATING = "heating"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    VENTILATION = "ventilation"
    OTHER = "other"


class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Action(str, Enum):
    AUTO_RESOLUTION = "auto_resolution"
    REQUEST_ADDITIONAL_INFO = "request_additional_info"
    SCHEDULE_INTERVENTION = "schedule_intervention"
    GENERATE_QUOTE = "generate_quote"
    ESCALATE_TO_HUMAN = "escalate_to_human"


class DecisionType(str, Enum):
    AI_ASSISTED = "ai_assisted"
    RULE_BASED = "rule_based"
    HUMAN_ESCALATED = "human_escalated"


class CompletenessStatus(str, Enum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
