from fastapi import APIRouter

from app.api.v1 import auth, metrics, tickets

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(tickets.router)
api_router.include_router(metrics.router)
