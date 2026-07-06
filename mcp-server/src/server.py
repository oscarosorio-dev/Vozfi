from mcp.server.fastmcp import FastMCP

from src.database import TransactionType
from src.tools import obtener_balance, obtener_resumen_por_categoria, registrar_transaccion

mcp = FastMCP("Vozfi-Core", host="0.0.0.0", port=8100)


@mcp.tool()
async def registrar_transaccion_tool(
    tipo: TransactionType,
    monto: float,
    categoria: str,
    descripcion: str | None = None,
) -> str:
    """
    Registra un ingreso o gasto en la base de datos de finanzas personales.

    tipo: 'income' para ingresos, 'expense' para gastos.
    monto: valor monetario positivo (ej: 25000.0).
    categoria: categoría de la transacción (ej: Comida, Transporte, Salario).
    descripcion: detalle opcional (ej: Café en Starbucks).

    Usa esta herramienta UNA SOLA VEZ por transacción mencionada. No la
    vuelvas a llamar después de recibir la confirmación.
    """
    if monto <= 0:
        return "Error: el monto debe ser mayor a 0."
    return registrar_transaccion(tipo, monto, categoria, descripcion)


@mcp.tool()
async def obtener_balance_tool() -> str:
    """Obtiene el balance financiero actual: total de ingresos, gastos y balance neto."""
    return obtener_balance()


@mcp.tool()
async def obtener_resumen_por_categoria_tool() -> str:
    """Obtiene el total de ingresos y gastos agrupados por categoría."""
    return obtener_resumen_por_categoria()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")