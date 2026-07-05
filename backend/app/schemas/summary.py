from app.models.transaction import TransactionType
from pydantic import BaseModel


class BalanceRead(BaseModel):
    income: float
    expense: float
    balance: float


class CategorySummaryItem(BaseModel):
    category: str
    type: TransactionType
    total: float