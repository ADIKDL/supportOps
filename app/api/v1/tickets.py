from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_db, require_org_roles
from app.jobs.queue import enqueue_triage
from app.models.enums import RoleEnum, TicketPriorityEnum, TicketStatusEnum
from app.schemas.comment import CommentCreate, CommentOut
from app.schemas.ticket import (
    AITicketInsightOut,
    TicketCreate,
    TicketListResponse,
    TicketOut,
    TicketUpdate,
    TriageEnqueueResponse,
)
from app.services import ticket_service

router = APIRouter(prefix="/orgs/{org_id}/tickets", tags=["tickets"])


@router.post("", response_model=TicketOut)
def create_ticket(
    org_id: int,
    payload: TicketCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(
        require_org_roles([RoleEnum.admin, RoleEnum.agent, RoleEnum.customer])
    ),
):
    return ticket_service.create_ticket(db, org_id, current_user.id, payload)


@router.get("", response_model=TicketListResponse)
def list_tickets(
    org_id: int,
    status: TicketStatusEnum | None = None,
    priority: TicketPriorityEnum | None = None,
    cursor: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
    membership=Depends(
        require_org_roles([RoleEnum.admin, RoleEnum.agent, RoleEnum.customer])
    ),
):
    items, next_cursor = ticket_service.list_tickets(db, org_id, status, priority, cursor, limit)
    return {"items": items, "next_cursor": next_cursor}


@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket(
    org_id: int,
    ticket_id: int,
    payload: TicketUpdate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(require_org_roles([RoleEnum.admin, RoleEnum.agent])),
):
    return ticket_service.update_ticket(db, org_id, ticket_id, current_user.id, payload)


@router.post("/{ticket_id}/comments", response_model=CommentOut)
def add_comment(
    org_id: int,
    ticket_id: int,
    payload: CommentCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(
        require_org_roles([RoleEnum.admin, RoleEnum.agent, RoleEnum.customer])
    ),
):
    return ticket_service.add_comment(db, org_id, ticket_id, current_user.id, payload.body)


@router.post("/{ticket_id}/ai/triage", response_model=TriageEnqueueResponse)
def enqueue_ai_triage(
    org_id: int,
    ticket_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(require_org_roles([RoleEnum.admin, RoleEnum.agent])),
):
    ticket_service.ensure_ticket_exists(db, org_id, ticket_id)
    return enqueue_triage(ticket_id=ticket_id, org_id=org_id, actor_id=current_user.id)


@router.get("/{ticket_id}/ai/triage", response_model=AITicketInsightOut)
def get_ai_triage(
    org_id: int,
    ticket_id: int,
    db=Depends(get_db),
    membership=Depends(
        require_org_roles([RoleEnum.admin, RoleEnum.agent, RoleEnum.customer])
    ),
):
    return ticket_service.get_ai_insight(db, org_id, ticket_id)
