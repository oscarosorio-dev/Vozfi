# Vozfi

![React](https://img.shields.io/badge/Expo-313131?style=flat&logo=expo)
![Vite](https://img.shields.io/badge/Yarn-313131?style=flat&logo=yarn)
![FastAPI](https://img.shields.io/badge/FastAPI-313131?style=flat&logo=fastapi)
![LangChain](https://img.shields.io/badge/LangGraph-313131?style=flat&logo=langgraph)
![Postgres](https://img.shields.io/badge/Postgres-313131?style=flat&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-313131?style=flat&logo=docker)
![Status](https://img.shields.io/badge/Status-development-success)

Fintech personal con voz como interfaz principal. Hablas, y un agente de IA registra tus ingresos/gastos o responde consultas sobre tu balance sin tocar un formulario.

## Arquitectura

```mermaid
flowchart TB

    A["Voz / Texto"]

    subgraph Mobile["Mobile App"]
        B["Expo (React Native)<br/>iOS / Android"]
    end

    subgraph Backend["Backend"]
        C["FastAPI<br/>Puerto 8000"]
    end

    D["STT (Groq)<br/>TTS (ElevenLabs)<br/>APIs nativas"]

    E["LLM (Groq)<br/>Tool Calling<br/>LangGraph (create_agent)"]

    subgraph MCP["MCP Server"]
        F["Puerto 8100<br/>Herramientas de negocio<br/>(CRUD, balance, resumen)"]
    end

    G[("PostgreSQL")]

    A --> B
    B -->|"REST<br/>(multipart / JSON)"| C

    D --> C
    C --> E
    E -->|"MCP (streamable-http)"| F

    C --> G
    F --> G
```

**Principio de diseño:** el agente LangGraph (`backend/app/agent/`) es el único núcleo de lógica de negocio conversacional. Los canales (`/agent/chat` para texto, `/voice/voice-input` para voz) son adaptadores delgados que traducen su modalidad a un mensaje de texto y reutilizan `run_agent()`. El agente decide, vía tool-calling contra el `mcp-server`, qué acción tomar (registrar, consultar, editar, eliminar) — ningún canal duplica esa lógica.

## Stack

| Componente | Tecnología |
|---|---|
| Backend | FastAPI, SQLAlchemy 2.0, Alembic, Postgres |
| Agente | LangGraph (`langchain.agents.create_agent`) + `langchain-mcp-adapters` |
| STT | Groq (Whisper, API nativa) |
| LLM (agente) | Groq (Llama 3.3, tool-calling) |
| TTS | ElevenLabs (API nativa) |
| MCP Server | `mcp[cli]` (FastMCP), streamable-http |
| Mobile | Expo (React Native), TypeScript, TanStack Query |

## Requisitos

- Docker + Docker Compose (backend, mcp-server, Postgres)
- Node.js 20+, Yarn y Expo CLI (`npx expo`) para el mobile app
- Cuentas/API keys: [Groq](https://console.groq.com/keys), [ElevenLabs](https://elevenlabs.io/app/settings/api-keys)

## Setup

1. Copiar variables de entorno:
   ```bash
   cp .env.example .env
   ```
   Completar `GROQ_API_KEY` y `ELEVENLABS_API_KEY`.

2. Levantar backend + mcp-server + Postgres:
   ```bash
   docker compose up --build
   ```
   El servicio `migrate` corre `alembic upgrade head` automáticamente antes de que `backend`/`mcp-server` arranquen (ver `docker-compose.yml`). Este compose es la configuración de **desarrollo** (bind mounts + hot-reload).

3. Levantar el mobile app:
   ```bash
   cd mobile
   cp env.example .env
   yarn install
   yarn start
   ```
   Ajusta `EXPO_PUBLIC_API_URL` en `mobile/.env` según tu entorno: `http://localhost:8000` (simulador iOS), `http://10.0.2.2:8000` (emulador Android) o la IP local de tu máquina (dispositivo físico).

## Variables de entorno

| Variable | Descripción |
|---|---|
| `GROQ_API_KEY` | STT (Whisper) + LLM del agente |
| `ELEVENLABS_API_KEY` | TTS |
| `GROQ_LLM_MODEL` | Modelo de chat del agente (default: `llama-3.3-70b-versatile`) |
| `MCP_SERVER_URL` | URL interna del mcp-server (default: `http://mcp-server:8100/mcp`) |
| `DATABASE_URL` | Conexión Postgres (formato `postgresql+psycopg://...`) |
| `CORS_ORIGINS` | Orígenes permitidos |

Ver `.env.example` (backend/mcp-server) y `mobile/env.example` (mobile) para el listado completo.

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/voice/voice-input` | Flujo completo: audio → STT → agente → TTS |
| `POST` | `/agent/chat` | Chat de texto con el agente financiero |
| `GET/POST/PATCH/DELETE` | `/transactions` | CRUD de transacciones |
| `GET` | `/summary/balance` | Balance total (ingresos, gastos, neto) |
| `GET` | `/summary/by-category` | Totales agrupados por categoría |
| `GET` | `/summary/by-month` | Totales agrupados por mes |
| `POST` | `/voice/transcribe` | STT aislado (debug) |
| `POST` | `/voice/synthesize` | TTS aislado (debug) |

Documentación interactiva: `http://localhost:8000/docs`.

## Tests

Requieren Postgres corriendo (integración real, no mocks de BD):

```bash
# Backend
cd backend
export DATABASE_URL="postgresql+psycopg://vozfi:vozfi@localhost:5432/vozfi"
uv run pytest tests/ -v

# mcp-server
cd mcp-server
export DATABASE_URL="postgresql+psycopg://vozfi:vozfi@localhost:5432/vozfi"
uv run pytest tests/ -v
```

O dentro de los contenedores: `docker compose exec backend pytest tests/ -v`.

## Despliegue a producción

`docker-compose.prod.yml` es la configuración de producción (sin bind mounts, con `healthcheck` y `restart: unless-stopped` en cada servicio):

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

- El mobile app se distribuye vía EAS Build (Expo) apuntando `EXPO_PUBLIC_API_URL` al backend desplegado.
- Rotar `GROQ_API_KEY`/`ELEVENLABS_API_KEY` como secretos del orquestador (no commitear `.env`).
- Postgres en el compose usa un volumen local; en producción real se recomienda un servicio gestionado (RDS, Cloud SQL, etc.) en vez del contenedor incluido.

## Decisiones de diseño y limitaciones conocidas

- **Postgres únicamente, sin abstracción multi-DB**: las queries usan funciones nativas de Postgres (`to_char`, enums nativos). Portabilidad a otro motor no es un requisito del proyecto.
- **Sin autenticación/multi-usuario**: es un sistema de un solo usuario por diseño; agregar auth es straightforward (JWT + `user_id` en `Transaction`) pero está fuera del alcance de este MVP.
- **mcp-server duplica el modelo `Transaction`** en vez de compartir código con el backend: es intencional — son dos servicios independientes (procesos, despliegues y `pyproject.toml` propios) que comparten la misma base de datos; acoplarlos a un mismo paquete Python rompería esa independencia.
- **`ToolCallLimitMiddleware(run_limit=1)`**: backstop estructural contra modelos que reintentan llamar tools tras completar la acción (loop de "auto-verificación" observado en producción con Llama 3.3 vía Groq) — solución estructural, no un parche de prompt.
- **Sin observabilidad estructurada** (tracing/métricas): logging estándar de Python es suficiente para el alcance actual; se agregaría (OpenTelemetry) si el proyecto creciera a multi-usuario real.