import enum

class TransactionType(str, enum.Enum):
    """Tipos de transacción permitidos en el sistema financiero."""
    INCOME = "income"    # Ingresos
    EXPENSE = "expense"  # Gastos