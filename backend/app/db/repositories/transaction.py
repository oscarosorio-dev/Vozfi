from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class TransactionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: TransactionCreate) -> Transaction:
        """Crea una transacción."""
        transaction = Transaction(**data.model_dump())
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get(self, transaction_id: uuid.UUID) -> Transaction | None:
        """Obtiene una transacción por su UUID exacto."""
        return self.db.get(Transaction, transaction_id)

    def find_by_description(self, query_text: str) -> Transaction | None:
        """
        Busca la transacción más reciente cuya descripción coincida parcialmente.
        Crucial para comandos rápidos por voz en LangGraph/MCP.
        """
        stmt = (
            select(Transaction)
            .where(Transaction.description.ilike(f"%{query_text.strip()}%"))
            .order_by(Transaction.occurred_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def update(self, transaction_id: uuid.UUID, data: TransactionUpdate) -> Transaction | None:
        """Actualiza una transacción."""
        transaction = self.get(transaction_id)
        if transaction is None:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(transaction, field, value)

        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def list(self, limit: int = 50, offset: int = 0, category: str | None = None, tx_type: TransactionType | None = None) -> list[Transaction]:
        """Lista transacciones ordenadas por fecha reciente con filtros opcionales."""
        stmt = select(Transaction).order_by(Transaction.occurred_at.desc())
        
        if category and category.strip():
            stmt = stmt.where(Transaction.category.ilike(f"%{category.strip()}%"))
        if tx_type:
            stmt = stmt.where(Transaction.type == tx_type)
            
        stmt = stmt.limit(limit).offset(offset)
        return list(self.db.scalars(stmt))

    def delete(self, transaction_id: uuid.UUID) -> bool:
        """Elimina una transacción de forma permanente."""
        transaction = self.get(transaction_id)
        if transaction is None:
            return False

        self.db.delete(transaction)
        self.db.commit()
        return True

    def get_balance(self, start: datetime | None = None, end: datetime | None = None) -> dict[str, float]:
        """Calcula totales de ingresos, gastos y balance neto."""
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
        """Retorna el total acumulado por cada categoría."""
        stmt = select(
            Transaction.category,
            Transaction.type,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        stmt = self._apply_date_filter(stmt, start, end)
        stmt = stmt.group_by(Transaction.category, Transaction.type).order_by(func.sum(Transaction.amount).desc())

        return [
            {"category": category, "type": tx_type.value, "total": float(total)}
            for category, tx_type, total in self.db.execute(stmt)
        ]

    def get_summary_by_month(self, start: datetime | None = None, end: datetime | None = None) -> list[dict]:
        """Muestra el resumen mensual sin abstracciones innecesarias."""
        month_expr = func.to_char(Transaction.occurred_at, "YYYY-MM")
        
        stmt = select(month_expr, Transaction.type, func.coalesce(func.sum(Transaction.amount), 0))
        stmt = self._apply_date_filter(stmt, start, end)
        stmt = stmt.group_by(month_expr, Transaction.type).order_by(month_expr)

        months: dict[str, dict[str, float]] = {}
        for month_str, tx_type, total in self.db.execute(stmt):
            months.setdefault(month_str, {"income": 0.0, "expense": 0.0})
            months[month_str][tx_type.value] = float(total)

        return [
            {
                "month": key,
                "income": totals["income"],
                "expense": totals["expense"],
                "balance": totals["income"] - totals["expense"],
            }
            for key, totals in sorted(months.items())
        ]

    @staticmethod
    def _apply_date_filter(stmt, start: datetime | None, end: datetime | None):
        if start is not None:
            stmt = stmt.where(Transaction.occurred_at >= start)
        if end is not None:
            stmt = stmt.where(Transaction.occurred_at <= end)
        return stmt