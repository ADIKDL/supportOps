from __future__ import annotations

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import APIError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.enums import RoleEnum
from app.models.membership import Membership
from app.models.user import User


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise APIError(401, "missing_token", "Missing Authorization header")

    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise APIError(401, "invalid_token", "Invalid or expired token")

    if payload.get("type") != "access":
        raise APIError(401, "invalid_token", "Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise APIError(401, "invalid_token", "Invalid token payload")

    user = db.get(User, int(user_id))
    if not user:
        raise APIError(401, "invalid_token", "User not found")

    return user


def get_membership(
    org_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Membership:
    membership = db.scalar(
        select(Membership).where(
            Membership.org_id == org_id,
            Membership.user_id == user.id,
        )
    )
    if not membership:
        raise APIError(403, "not_member", "Not a member of this organization")
    return membership


def require_org_roles(allowed_roles: list[RoleEnum]):
    def _dependency(membership: Membership = Depends(get_membership)) -> Membership:
        if membership.role not in allowed_roles:
            raise APIError(403, "forbidden", "Insufficient role for this action")
        return membership

    return _dependency
