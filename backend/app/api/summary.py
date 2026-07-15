from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.repositories.transaction import TransactionRepository
from app.db.session import get_db
from app.schemas.summary import BalanceRead, CategorySummaryItem, MonthlySummaryItem

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/balance", response_model=BalanceRead)
def get_balance(
    start: datetime | None = None,
    end: datetime | None = None,
    db: Session = Depends(get_db),
) -> BalanceRead:
    return TransactionRepository(db).get_balance(start=start, end=end)


@router.get("/by-category", response_model=list[CategorySummaryItem])
def get_summary_by_category(
    start: datetime | None = None,
    end: datetime | None = None,
    db: Session = Depends(get_db),
) -> list[CategorySummaryItem]:
    return TransactionRepository(db).get_summary_by_category(start=start, end=end)


@router.get("/by-month", response_model=list[MonthlySummaryItem])
def get_summary_by_month(
    start: datetime | None = None,
    end: datetime | None = None,
    db: Session = Depends(get_db),
) -> list[MonthlySummaryItem]:
    return TransactionRepository(db).get_summary_by_month(start=start, end=end)