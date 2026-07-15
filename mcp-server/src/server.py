from mcp.server.fastmcp import FastMCP

from src.database import TransactionType
from src.tools import (
    actualizar_transaccion,
    eliminar_transaccion,
    listar_transacciones,
    obtener_balance,
    obtener_resumen_por_categoria,
    registrar_transaccion,
    vaciar_transacciones,
)

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


@mcp.tool()
async def listar_transacciones_tool(
    limite: int = 10,
    categoria: str | None = None,
    tipo: TransactionType | None = None,
) -> str:
    """
    Lista las transacciones recientes para que puedas obtener el ID antes de modificarlas o eliminarlas.
    Permite filtrar los resultados por categoría o tipo (ingreso/gasto).
    """
    return listar_transacciones(limite, categoria, tipo)


@mcp.tool()
async def actualizar_transaccion_tool(
    id_transaccion: str | None = None,
    descripcion_busqueda: str | None = None,
    tipo: TransactionType | None = None,
    monto: float | None = None,
    categoria: str | None = None,
    descripcion: str | None = None,
) -> str:
    """
    Actualiza una transacción existente. Se debe proveer obligatoriamente
    el id_transaccion o la descripcion_busqueda para identificar el registro.

    id_transaccion: El ID único (UUID) si ya se conoce previamente.
    descripcion_busqueda: Texto aproximado o palabra clave (ej: 'café', 'taxi') para buscar la
                          transacción más reciente que coincida, útil en comandos rápidos por voz.
    tipo: Nuevo tipo ('income' o 'expense') si se desea cambiar.
    monto: Nuevo valor monetario positivo si se desea corregir.
    categoria: Nueva categoría si se desea reclasificar.
    descripcion: Nuevo detalle de texto si se desea modificar el comentario original.
    """
    return actualizar_transaccion(
        id_transaccion=id_transaccion,
        descripcion_busqueda=descripcion_busqueda,
        tipo=tipo,
        monto=monto,
        categoria=categoria,
        descripcion=descripcion
    )


@mcp.tool()
async def eliminar_transaccion_tool(
    id_transaccion: str | None = None,
    descripcion_busqueda: str | None = None,
) -> str:
    """
    Elimina permanentemente una transacción de la base de datos.
    Se debe proveer obligatoriamente el id_transaccion o la descripcion_busqueda.

    id_transaccion: El ID único (UUID) si ya se conoce previamente.
    descripcion_busqueda: Texto aproximado o palabra clave (ej: 'almuerzo') para buscar y borrar
                          la transacción más reciente que coincida, ideal para flujos ágiles por voz.
    """
    return eliminar_transaccion(id_transaccion=id_transaccion, descripcion_busqueda=descripcion_busqueda)


@mcp.tool()
async def vaciar_transacciones_tool(confirmar: bool = False) -> str:
    """
    Elimina ABSOLUTAMENTE TODAS las transacciones de la base de datos (reinicio completo).
    Esta acción es irreversible y destructiva.

    confirmar: Por seguridad, este parámetro inicia en False. 
               - El asistente DEBE preguntar explícitamente al usuario si está seguro de realizar 
                 esta acción antes de llamar a esta herramienta con confirmar=True.
               - Si el usuario aún no ha dado su consentimiento verbal o escrito explícito para borrar todo, 
                 llama a esta herramienta con confirmar=False para obtener el mensaje de advertencia.
    """
    return vaciar_transacciones(confirmar)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
