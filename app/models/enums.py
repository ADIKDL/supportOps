from enum import Enum


class RoleEnum(str, Enum):
    admin = "admin"
    agent = "agent"
    customer = "customer"


class TicketStatusEnum(str, Enum):
    new = "new"
    open = "open"
    pending = "pending"
    resolved = "resolved"


class TicketPriorityEnum(str, Enum):
    low = "low"
    med = "med"
    high = "high"
    urgent = "urgent"


class AICategoryEnum(str, Enum):
    billing = "billing"
    bug = "bug"
    feature = "feature"
    other = "other"
