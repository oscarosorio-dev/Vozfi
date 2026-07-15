import uuid
from datetime import UTC, datetime
from sqlalchemy import Enum, Float, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import TransactionType

class Transaction(Base):
    """
    Modelo ORM que representa una transacción financiera (Gasto o Ingreso).
    """
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    type: Mapped[TransactionType] = mapped_column(
        Enum(
            TransactionType, 
            name="transaction_type", 
            native_enum=True, 
            values_callable=lambda x: [e.value for e in x]
        ), 
        nullable=False, 
        index=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    
    # Añadimos la columna faltante mapeada a la fecha de creación
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        default=lambda: datetime.now(UTC), 
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Transaction {self.type.value.upper()} | {self.category}: {self.amount:.2f}>"