from fastapi import APIRouter

from app.api import health, summary, transactions, voice

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(transactions.router)
api_router.include_router(summary.router)
api_router.include_router(voice.router)