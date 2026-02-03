from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import APIError
from app.models.ai_ticket_insight import AITicketInsight
from app.models.comment import Comment
from app.models.enums import TicketPriorityEnum, TicketStatusEnum
from app.models.membership import Membership
from app.models.ticket import Ticket
from app.services import audit_service


def ensure_ticket_exists(db: Session, org_id: int, ticket_id: int) -> Ticket:
    ticket = db.scalar(
        select(Ticket).where(Ticket.id == ticket_id, Ticket.org_id == org_id)
    )
    if not ticket:
        raise APIError(404, "ticket_not_found", "Ticket not found")
    return ticket


def create_ticket(db: Session, org_id: int, actor_id: int, payload) -> Ticket:
    ticket = Ticket(
        org_id=org_id,
        created_by=actor_id,
        subject=payload.subject,
        body=payload.body,
        priority=payload.priority or TicketPriorityEnum.med,
        status=TicketStatusEnum.new,
    )
    db.add(ticket)
    db.flush()

    audit_service.log(
        db=db,
        org_id=org_id,
        actor_id=actor_id,
        action="ticket_created",
        entity_type="ticket",
        entity_id=ticket.id,
        metadata={"priority": ticket.priority.value},
    )

    db.commit()
    db.refresh(ticket)
    return ticket


def list_tickets(
    db: Session,
    org_id: int,
    status: TicketStatusEnum | None,
    priority: TicketPriorityEnum | None,
    cursor: int | None,
    limit: int,
) -> tuple[list[Ticket], int | None]:
    query = select(Ticket).where(Ticket.org_id == org_id)
    if status:
        query = query.where(Ticket.status == status)
    if priority:
        query = query.where(Ticket.priority == priority)
    if cursor:
        query = query.where(Ticket.id < cursor)

    query = query.order_by(Ticket.id.desc()).limit(limit)
    items = list(db.scalars(query).all())
    next_cursor = items[-1].id if len(items) == limit else None
    return items, next_cursor


def update_ticket(db: Session, org_id: int, ticket_id: int, actor_id: int, payload) -> Ticket:
    ticket = ensure_ticket_exists(db, org_id, ticket_id)
    updates = {}
    fields = payload.model_fields_set

    if "status" in fields:
        ticket.status = payload.status
        updates["status"] = payload.status.value if payload.status else None
    if "priority" in fields:
        ticket.priority = payload.priority
        updates["priority"] = payload.priority.value if payload.priority else None
    if "assigned_to" in fields:
        if payload.assigned_to is not None:
            membership = db.scalar(
                select(Membership).where(
                    Membership.org_id == org_id,
                    Membership.user_id == payload.assigned_to,
                )
            )
            if not membership:
                raise APIError(400, "invalid_assignee", "Assignee is not in this org")
        ticket.assigned_to = payload.assigned_to
        updates["assigned_to"] = payload.assigned_to

    if not updates:
        return ticket

    ticket.updated_at = datetime.now(timezone.utc)

    audit_service.log(
        db=db,
        org_id=org_id,
        actor_id=actor_id,
        action="ticket_updated",
        entity_type="ticket",
        entity_id=ticket.id,
        metadata=updates,
    )

    db.commit()
    db.refresh(ticket)
    return ticket


def add_comment(
    db: Session, org_id: int, ticket_id: int, actor_id: int, body: str
) -> Comment:
    ticket = ensure_ticket_exists(db, org_id, ticket_id)

    comment = Comment(ticket_id=ticket.id, author_id=actor_id, body=body)
    db.add(comment)
    db.flush()

    audit_service.log(
        db=db,
        org_id=org_id,
        actor_id=actor_id,
        action="comment_created",
        entity_type="comment",
        entity_id=comment.id,
        metadata={"ticket_id": ticket.id},
    )

    db.commit()
    db.refresh(comment)
    return comment


def get_ai_insight(db: Session, org_id: int, ticket_id: int) -> AITicketInsight:
    ticket = ensure_ticket_exists(db, org_id, ticket_id)
    insight = db.scalar(
        select(AITicketInsight).where(AITicketInsight.ticket_id == ticket.id)
    )
    if not insight:
        raise APIError(404, "insight_not_found", "AI triage not found")
    return insight
