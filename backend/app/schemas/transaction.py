import uuid
from datetime import UTC, datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.models.enums import TransactionType

class TransactionBase(BaseModel):
    type: TransactionType = Field(..., description="Tipo de movimiento: 'income' o 'expense'")
    amount: float = Field(..., description="Monto de la transacción, debe ser estrictamente positivo")
    category: str = Field(..., max_length=50, description="Categoría del movimiento")
    description: str | None = Field(None, max_length=255, description="Detalle opcional de la transacción")
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Fecha/hora en que ocurrió la transacción (default: ahora, si no se especifica)",
    )

    @field_validator("amount")
    @classmethod
    def validar_monto_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("El monto debe ser mayor a 0.")
        return v

    @field_validator("category")
    @classmethod
    def limpiar_categoria(cls, v: str) -> str:
        v_limpio = v.strip()
        if not v_limpio:
            raise ValueError("La categoría no puede estar vacía.")
        return v_limpio

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    type: TransactionType | None = Field(None)
    amount: float | None = Field(None)
    category: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=255)

    @field_validator("amount")
    @classmethod
    def validar_monto_positivo(cls, v: float | None) -> float | None:
        if v is not None and v <= 0:
            raise ValueError("El monto de actualización debe ser mayor a 0.")
        return v

class TransactionRead(TransactionBase):
    id: uuid.UUID
    occurred_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)