# Vozfi — Backend

API FastAPI que expone el pipeline de voz (STT → agente → TTS), el chat de texto con el agente, y el CRUD de transacciones. Ver el [README raíz](../README.md) para la arquitectura completa del proyecto.

## Responsabilidad

- Orquesta STT (Groq) y TTS (ElevenLabs) como servicios de I/O.
- Aloja al agente conversacional (LangGraph `create_agent`), que es el único punto donde vive la lógica de negocio.
- El agente accede a las herramientas de negocio (registrar/consultar/editar/eliminar transacciones) vía MCP contra el `mcp-server`, no directamente contra la base de datos.
- Expone además un CRUD REST convencional de transacciones (`/transactions`) y resúmenes (`/summary/*`) para consumo directo de clientes (el mobile app los usa para listados/gráficos, sin pasar por el agente).

## Correr aislado

```bash
uv sync --all-groups
export DATABASE_URL="postgresql+psycopg://vozfi:vozfi@localhost:5432/vozfi"
export GROQ_API_KEY=...
export ELEVENLABS_API_KEY=...
export MCP_SERVER_URL="http://localhost:8100/mcp"

uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Requiere Postgres y el `mcp-server` corriendo por separado (ver `docker-compose.yml` en la raíz para levantar todo junto).

## Tests

```bash
export DATABASE_URL="postgresql+psycopg://vozfi:vozfi@localhost:5432/vozfi"
uv run pytest tests/ -v
```

## Estructura

```
app/
  agent/      # grafo LangGraph + servicio run_agent (núcleo conversacional)
  api/        # routers FastAPI (adapters delgados, sin lógica de negocio)
  core/       # config, excepciones, mapeo de errores HTTP
  db/         # modelos SQLAlchemy, sesión, repositorios
  schemas/    # contratos Pydantic
  services/   # clientes de STT/TTS (Groq, ElevenLabs)
alembic/      # migraciones
tests/        # integración contra Postgres real
```