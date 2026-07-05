from fastapi import APIRouter

from app.api import health, transactions

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(transactions.router)