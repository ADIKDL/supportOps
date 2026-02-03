from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AICategoryEnum


class AITicketInsight(Base):
    __tablename__ = "ai_ticket_insights"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), unique=True, nullable=False)
    category: Mapped[AICategoryEnum] = mapped_column(
        SAEnum(AICategoryEnum, name="ai_category_enum", native_enum=False),
        nullable=False,
    )
    urgency_score: Mapped[int] = mapped_column(nullable=False)
    suggested_reply: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    ticket = relationship("Ticket", back_populates="ai_insight")
