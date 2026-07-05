import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, name="transaction_type", values_callable=lambda e: [m.value for m in e])
    )
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    category: Mapped[str] = mapped_column(String(64))
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())