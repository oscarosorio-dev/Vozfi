# Vozfi — MCP Server

Servidor MCP (Model Context Protocol) que expone las herramientas de negocio de Vozfi como funciones invocables por el agente de IA. Ver el [README raíz](../README.md) para la arquitectura completa.

## Responsabilidad

Único punto de acceso a la tabla `transactions` para operaciones de negocio (el CRUD REST del backend accede directamente, pero todo lo que pasa por el **agente conversacional** — voz o texto — pasa por acá). Expone:

- `registrar_transaccion_tool` — crea un ingreso o gasto.
- `obtener_balance_tool` — balance total (ingresos, gastos, neto).
- `obtener_resumen_por_categoria_tool` — totales por categoría.
- `listar_transacciones_tool` — búsqueda por texto/categoría.
- `actualizar_transaccion_tool` / `eliminar_transaccion_tool` — edición puntual.
- `vaciar_transacciones_tool` — borrado masivo, con guardrail de confirmación explícita.

Transporte: `streamable-http` (puerto 8100), vía el SDK oficial `mcp[cli]` (`FastMCP`).

## Por qué es un servicio separado

Es un proceso, despliegue y `pyproject.toml` independientes del backend. Comparte la misma base de datos Postgres pero **no comparte código** con el backend — duplica el modelo `Transaction` mínimo necesario a propósito, para no acoplar dos servicios que deben poder evolucionar y desplegarse por separado.

## Correr aislado

```bash
uv sync --all-groups
export DATABASE_URL="postgresql+psycopg://vozfi:vozfi@localhost:5432/vozfi"
uv run python -m src.server
```

Requiere que la tabla `transactions` ya exista (creada por las migraciones de Alembic del backend — no tiene migraciones propias).

## Tests

```bash
export DATABASE_URL="postgresql+psycopg://vozfi:vozfi@localhost:5432/vozfi"
uv run pytest tests/ -v
```

## Estructura

```
src/
  server.py    # definición de tools MCP (FastMCP)
  tools.py     # lógica de negocio de cada tool
  database.py  # modelo Transaction (duplicado, minimal) + sesión
tests/
```