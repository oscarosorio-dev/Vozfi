import uuid
from contextlib import contextmanager
from datetime import UTC, datetime

from sqlalchemy import func, select, delete

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
    descripcion: str | None = None,
) -> str:
    """Crea una transacción (ingreso o gasto) y retorna un mensaje de confirmación."""
    if monto <= 0:
        return "Error: El monto de la transacción debe ser mayor a 0."
        
    categoria_limpia = categoria.strip()
    if not categoria_limpia:
        return "Error: La categoría no puede estar vacía."

    with _session() as session:
        transaction = Transaction(
            type=tipo,
            amount=abs(monto),
            category=categoria_limpia,
            description=descripcion.strip() if descripcion else None,
            occurred_at=datetime.now(UTC),
        )
        session.add(transaction)
        session.commit()

        verbo = "ingreso" if tipo == TransactionType.INCOME else "gasto"
        detalle = f" ({descripcion})" if descripcion else ""
        return f"Registrado un {verbo} de {monto:.2f} en '{categoria_limpia}'{detalle}."


def obtener_balance() -> str:
    """Calcula ingresos, gastos y balance neto totales dinámicamente."""
    with _session() as session:
        stmt = select(Transaction.type, func.coalesce(func.sum(Transaction.amount), 0)).group_by(Transaction.type)
        totals = dict.fromkeys(TransactionType, 0.0)
        for tx_type, total in session.execute(stmt):
            totals[tx_type] = float(total)

        income = totals[TransactionType.INCOME]
        expense = totals[TransactionType.EXPENSE]
        return f"Ingresos totales: {income:.2f}. Gastos totales: {expense:.2f}. Balance neto disponible: {income - expense:.2f}."


def obtener_resumen_por_categoria() -> str:
    """Retorna el total gastado/ingresado por cada categoría de forma descendente."""
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


def listar_transacciones(
    limite: int = 10,
    categoria: str | None = None,
    tipo: TransactionType | None = None,
) -> str:
    """Lista las transacciones ordenadas por fecha de ocurrencia (de más reciente a más antigua)."""
    with _session() as session:
        stmt = select(Transaction).order_by(Transaction.occurred_at.desc())
        
        if categoria and categoria.strip():
            stmt = stmt.where(Transaction.category.ilike(f"%{categoria.strip()}%"))
        if tipo:
            stmt = stmt.where(Transaction.type == tipo)
            
        stmt = stmt.limit(limite)
        results = session.execute(stmt).scalars().all()

        if not results:
            return "No se encontraron transacciones con los criterios especificados."

        lineas = []
        for tx in results:
            desc = f" | Descripción: {tx.description}" if tx.description else ""
            fecha = tx.occurred_at.strftime("%Y-%m-%d %H:%M")
            lineas.append(
                f"ID: {tx.id} | Fecha: {fecha} | {tx.type.value.upper()}: {tx.amount:.2f} | Categoría: {tx.category}{desc}"
            )
        return "\n".join(lineas)


def eliminar_transaccion(id_transaccion: str | None = None, descripcion_busqueda: str | None = None) -> str:
    """
    Elimina una transacción por su ID UUID exacto. 
    Si no se provee un ID, permite buscar por descripción aproximada para flujos de voz ágiles.
    """
    with _session() as session:
        tx = None
        
        if id_transaccion and id_transaccion.strip():
            try:
                tx_id = uuid.UUID(id_transaccion.strip())
                stmt = select(Transaction).where(Transaction.id == tx_id)
                tx = session.execute(stmt).scalar_one_or_none()
            except ValueError:
                return f"Error: El ID '{id_transaccion}' no es un UUID válido."
        
        elif descripcion_busqueda and descripcion_busqueda.strip():
            stmt = (
                select(Transaction)
                .where(Transaction.description.ilike(f"%{descripcion_busqueda.strip()}%"))
                .order_by(Transaction.occurred_at.desc())
                .limit(1)
            )
            tx = session.execute(stmt).scalar_one_or_none()
            if not tx:
                return f"Error: No se encontró ninguna transacción reciente que coincida con '{descripcion_busqueda}'."
        else:
            return "Error: Debes proporcionar el 'id_transaccion' o una 'descripcion_busqueda' para eliminar."

        if not tx:
            return f"Error: No se encontró la transacción especificada."

        tipo_str = "ingreso" if tx.type == TransactionType.INCOME else "gasto"
        monto_str = tx.amount
        cat_str = tx.category

        session.delete(tx)
        session.commit()
        return f"Éxito: Se eliminó correctamente el {tipo_str} de {monto_str:.2f} en la categoría '{cat_str}'."


def actualizar_transaccion(
    id_transaccion: str | None = None,
    descripcion_busqueda: str | None = None,
    tipo: TransactionType | None = None,
    monto: float | None = None,
    categoria: str | None = None,
    descripcion: str | None = None,
) -> str:
    """
    Actualiza selectivamente los campos de una transacción.
    Soporta búsqueda directa por ID o búsqueda semántica por descripción reciente.
    """
    if monto is not None and monto <= 0:
        return "Error: El monto de actualización debe ser mayor a 0."

    with _session() as session:
        tx = None
        
        if id_transaccion and id_transaccion.strip():
            try:
                tx_id = uuid.UUID(id_transaccion.strip())
                stmt = select(Transaction).where(Transaction.id == tx_id)
                tx = session.execute(stmt).scalar_one_or_none()
            except ValueError:
                return f"Error: El ID '{id_transaccion}' no es un UUID válido."
        elif descripcion_busqueda and descripcion_busqueda.strip():
            stmt = (
                select(Transaction)
                .where(Transaction.description.ilike(f"%{descripcion_busqueda.strip()}%"))
                .order_by(Transaction.occurred_at.desc())
                .limit(1)
            )
            tx = session.execute(stmt).scalar_one_or_none()
        else:
            return "Error: Se requiere 'id_transaccion' o 'descripcion_busqueda' para identificar el registro."

        if not tx:
            return "Error: No se encontró la transacción solicitada para actualizar."

        cambios = []
        if tipo is not None:
            tx.type = tipo
            cambios.append(f"tipo a '{tipo.value}'")
            
        if monto is not None:
            tx.amount = abs(monto)
            cambios.append(f"monto a {monto:.2f}")
            
        if categoria is not None and categoria.strip():
            tx.category = categoria.strip()
            cambios.append(f"categoría a '{tx.category}'")
            
        if descripcion is not None:
            descripcion_limpia = descripcion.strip()
            tx.description = descripcion_limpia if descripcion_limpia else None
            cambios.append(f"descripción a '{tx.description}'")

        if not cambios:
            return "No se realizaron cambios (los campos enviados estaban vacíos o idénticos)."

        session.commit()
        return f"Transacción actualizada exitosamente. Cambios aplicados: " + ", ".join(cambios) + "."


def vaciar_transacciones(confirmar: bool = False) -> str:
    """Elimina permanentemente todas las transacciones bajo confirmación explícita."""
    if not confirmar:
        return (
            "ADVERTENCIA: Esta acción es destructiva e irreversible. Eliminará permanentemente "
            "todas las transacciones de la base de datos. "
            "Si estás seguro, vuelve a ejecutar pasando 'confirmar=True'."
        )

    with _session() as session:
        stmt = delete(Transaction)
        result = session.execute(stmt)
        session.commit()
        
        cant_eliminada = result.rowcount
        if cant_eliminada == 0:
            return "No había transacciones registradas para eliminar."
            
        return f"Se han eliminado correctamente todas las transacciones de la base de datos ({cant_eliminada} registros eliminados)."
