from pydantic import BaseModel

from app.models.transaction import TransactionType


class BalanceRead(BaseModel):
    income: float
    expense: float
    balance: float


class CategorySummaryItem(BaseModel):
    category: str
    type: TransactionType
    total: float


class MonthlySummaryItem(BaseModel):
    month: str
    income: float
    expense: float
    balance: float