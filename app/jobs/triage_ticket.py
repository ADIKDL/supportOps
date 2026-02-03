from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.ai_ticket_insight import AITicketInsight
from app.models.ticket import Ticket
from app.services import ai_service, audit_service

logger = logging.getLogger(__name__)


def triage_ticket_job(ticket_id: int, org_id: int, actor_id: int) -> int:
    db: Session = SessionLocal()
    try:
        ticket = db.scalar(select(Ticket).where(Ticket.id == ticket_id))
        if not ticket or ticket.org_id != org_id:
            raise ValueError("Ticket not found for org")

        insight = db.scalar(
            select(AITicketInsight).where(AITicketInsight.ticket_id == ticket_id)
        )
        now = datetime.now(timezone.utc)

        if insight:
            last = insight.updated_at or insight.created_at
            if last and now - last < timedelta(hours=24):
                logger.info("Skipping AI triage for ticket %s (recent insight)", ticket_id)
                return insight.id

        provider = ai_service.get_provider()
        result = provider.triage(ticket)

        if insight:
            insight.category = result.category
            insight.urgency_score = result.urgency_score
            insight.suggested_reply = result.suggested_reply
            insight.model = provider.model_name
            insight.updated_at = now
        else:
            insight = AITicketInsight(
                ticket_id=ticket.id,
                category=result.category,
                urgency_score=result.urgency_score,
                suggested_reply=result.suggested_reply,
                model=provider.model_name,
            )
            db.add(insight)

        db.flush()

        audit_service.log(
            db=db,
            org_id=org_id,
            actor_id=actor_id,
            action="ai_triage",
            entity_type="ticket",
            entity_id=ticket.id,
            metadata={"model": provider.model_name},
        )

        db.commit()
        return insight.id
    except Exception:
        db.rollback()
        logger.exception("AI triage job failed for ticket %s", ticket_id)
        raise
    finally:
        db.close()
