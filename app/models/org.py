from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Org(Base):
    __tablename__ = "orgs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    memberships = relationship("Membership", back_populates="org", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="org", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="org", cascade="all, delete-orphan")
