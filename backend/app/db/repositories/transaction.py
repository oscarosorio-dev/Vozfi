import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
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