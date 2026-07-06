from contextlib import contextmanager
from datetime import UTC, datetime

from sqlalchemy import func, select

from src.database import SessionLocal, Transaction, TransactionType


@contextmanager
def _session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def registrar_transaccion(
    tipo: TransactionType,
    monto: float,
    categoria: str,
    descripcion: str | None,
) -> str:
    """Crea una transacción (ingreso o gasto) y retorna un mensaje de confirmación."""
    with _session() as session:
        transaction = Transaction(
            type=tipo,
            amount=monto,
            category=categoria,
            description=descripcion,
            occurred_at=datetime.now(UTC),
        )
        session.add(transaction)
        session.commit()

        verbo = "ingreso" if tipo == TransactionType.INCOME else "gasto"
        return f"Registrado un {verbo} de {monto:.2f} en '{categoria}'."


def obtener_balance() -> str:
    """Calcula ingresos, gastos y balance neto totales."""
    with _session() as session:
        stmt = select(Transaction.type, func.coalesce(func.sum(Transaction.amount), 0)).group_by(Transaction.type)
        totals = dict.fromkeys(TransactionType, 0.0)
        for tx_type, total in session.execute(stmt):
            totals[tx_type] = float(total)

        income = totals[TransactionType.INCOME]
        expense = totals[TransactionType.EXPENSE]
        return f"Ingresos: {income:.2f}. Gastos: {expense:.2f}. Balance neto: {income - expense:.2f}."


def obtener_resumen_por_categoria() -> str:
    """Retorna el total gastado/ingresado por cada categoría."""
    with _session() as session:
        stmt = (
            select(Transaction.category, Transaction.type, func.coalesce(func.sum(Transaction.amount), 0))
            .group_by(Transaction.category, Transaction.type)
            .order_by(func.sum(Transaction.amount).desc())
        )
        rows = session.execute(stmt).all()

        if not rows:
            return "No hay transacciones registradas todavía."

        lineas = [f"- {categoria} ({tipo.value}): {total:.2f}" for categoria, tipo, total in rows]
        return "\n".join(lineas)