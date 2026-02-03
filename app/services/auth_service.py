from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import APIError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
    verify_refresh_token_hash,
)
from app.models.enums import RoleEnum
from app.models.membership import Membership
from app.models.org import Org
from app.models.user import User


def register_user(db: Session, payload) -> tuple[User, Org, dict]:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise APIError(400, "email_taken", "Email already registered")

    org_name = payload.org_name or payload.email.split("@", 1)[0]

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    org = Org(name=org_name)

    db.add_all([user, org])
    db.flush()

    membership = Membership(user_id=user.id, org_id=org.id, role=RoleEnum.admin)
    db.add(membership)
    db.commit()
    db.refresh(user)

    tokens = issue_tokens(db, user)
    return user, org, tokens


def authenticate_user(db: Session, email: str, password: str) -> dict:
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        raise APIError(401, "invalid_credentials", "Invalid email or password")

    return issue_tokens(db, user)


def refresh_tokens(db: Session, refresh_token: str) -> dict:
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise APIError(401, "invalid_token", "Invalid refresh token")

    if payload.get("type") != "refresh":
        raise APIError(401, "invalid_token", "Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise APIError(401, "invalid_token", "Invalid token payload")

    user = db.get(User, int(user_id))
    if not user:
        raise APIError(401, "invalid_token", "User not found")

    if not verify_refresh_token_hash(refresh_token, user.refresh_token_hash):
        raise APIError(401, "invalid_token", "Refresh token mismatch")

    return issue_tokens(db, user)


def issue_tokens(db: Session, user: User) -> dict:
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    user.refresh_token_hash = hash_refresh_token(refresh_token)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
