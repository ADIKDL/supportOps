from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AICategoryEnum, TicketPriorityEnum, TicketStatusEnum


class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=255)
    body: str = Field(min_length=1)
    priority: TicketPriorityEnum | None = None


class TicketUpdate(BaseModel):
    status: TicketStatusEnum | None = None
    priority: TicketPriorityEnum | None = None
    assigned_to: int | None = None


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    created_by: int
    assigned_to: int | None
    status: TicketStatusEnum
    priority: TicketPriorityEnum
    subject: str
    body: str
    created_at: datetime
    updated_at: datetime | None


class TicketListResponse(BaseModel):
    items: list[TicketOut]
    next_cursor: int | None


class AITicketInsightOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    category: AICategoryEnum
    urgency_score: int
    suggested_reply: str
    model: str
    created_at: datetime
    updated_at: datetime | None


class TriageEnqueueResponse(BaseModel):
    status: str
    job_id: str | None = None
