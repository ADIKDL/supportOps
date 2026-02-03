from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ai_ticket_insight import AITicketInsight
from app.models.enums import AICategoryEnum, TicketStatusEnum
from app.models.ticket import Ticket


def get_metrics(db: Session, org_id: int) -> dict:
    by_status = {status.value: 0 for status in TicketStatusEnum}
    status_rows = db.execute(
        select(Ticket.status, func.count()).where(Ticket.org_id == org_id).group_by(Ticket.status)
    ).all()
    for status, count in status_rows:
        by_status[status.value] = count

    by_category = {category.value: 0 for category in AICategoryEnum}
    category_rows = db.execute(
        select(AITicketInsight.category, func.count())
        .join(Ticket, Ticket.id == AITicketInsight.ticket_id)
        .where(Ticket.org_id == org_id)
        .group_by(AITicketInsight.category)
    ).all()
    for category, count in category_rows:
        by_category[category.value] = count

    threshold = datetime.now(timezone.utc) - timedelta(hours=48)
    open_statuses = [
        TicketStatusEnum.new,
        TicketStatusEnum.open,
        TicketStatusEnum.pending,
    ]
    open_over_48h = (
        db.scalar(
            select(func.count())
            .select_from(Ticket)
            .where(
                Ticket.org_id == org_id,
                Ticket.status.in_(open_statuses),
                Ticket.created_at < threshold,
            )
        )
        or 0
    )

    return {
        "by_status": by_status,
        "by_category": by_category,
        "sla": {"open_over_48h": int(open_over_48h)},
    }
