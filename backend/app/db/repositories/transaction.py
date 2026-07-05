from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import TransactionCreate


class TransactionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: TransactionCreate) -> Transaction:
        transaction = Transaction(**data.model_dump())
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get(self, transaction_id: uuid.UUID) -> Transaction | None:
        return self.db.get(Transaction, transaction_id)

    def list(self, limit: int = 50, offset: int = 0) -> list[Transaction]:
        stmt = select(Transaction).order_by(Transaction.occurred_at.desc()).limit(limit).offset(offset)
        return list(self.db.scalars(stmt))

    def delete(self, transaction_id: uuid.UUID) -> bool:
        transaction = self.get(transaction_id)
        if transaction is None:
            return False
        self.db.delete(transaction)
        self.db.commit()
        return True

    def get_balance(self, start: datetime | None = None, end: datetime | None = None) -> dict[str, float]:
        stmt = select(Transaction.type, func.coalesce(func.sum(Transaction.amount), 0))
        stmt = self._apply_date_filter(stmt, start, end)
        stmt = stmt.group_by(Transaction.type)

        totals = {t: 0.0 for t in TransactionType}
        for tx_type, total in self.db.execute(stmt):
            totals[tx_type] = float(total)

        income = totals[TransactionType.INCOME]
        expense = totals[TransactionType.EXPENSE]
        return {"income": income, "expense": expense, "balance": income - expense}

    def get_summary_by_category(self, start: datetime | None = None, end: datetime | None = None) -> list[dict]:
        stmt = select(
            Transaction.category,
            Transaction.type,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        stmt = self._apply_date_filter(stmt, start, end)
        stmt = stmt.group_by(Transaction.category, Transaction.type).order_by(func.sum(Transaction.amount).desc())

        return [
            {"category": category, "type": tx_type, "total": float(total)}
            for category, tx_type, total in self.db.execute(stmt)
        ]

    @staticmethod
    def _apply_date_filter(stmt, start: datetime | None, end: datetime | None):
        if start is not None:
            stmt = stmt.where(Transaction.occurred_at >= start)
        if end is not None:
            stmt = stmt.where(Transaction.occurred_at <= end)
        return stmt