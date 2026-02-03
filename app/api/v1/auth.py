from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_db
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserOut
from app.services import auth_service

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db=Depends(get_db)):
    user, org, tokens = auth_service.register_user(db, payload)
    return tokens


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db=Depends(get_db)):
    tokens = auth_service.authenticate_user(db, payload.email, payload.password)
    return tokens


@router.post("/auth/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db=Depends(get_db)):
    tokens = auth_service.refresh_tokens(db, payload.refresh_token)
    return tokens


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user
