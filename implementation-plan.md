# Implementation Plan: VozFinanzas - Asistente de Finanzas por Voz

## Objetivo del Proyecto y Propuesta de Valor

**VozFinanzas** es un asistente personal de finanzas impulsado por voz que permite registrar ingresos y gastos mediante comandos de voz naturales y obtener resúmenes, balances y detalles mediante consultas habladas. 

**Propuesta de valor**:
- Interacción completamente hands-free (ideal para multitarea).
- Procesamiento inteligente de lenguaje natural para categorizar transacciones automáticamente.
- Resúmenes accionables por voz (balance actual, gastos por mes/categoría).
- Demostración técnica sólida de IA multimodal (STT + LLM + TTS) combinada con full-stack moderno.
- Caso de uso real y relatable que resalta habilidades demandadas en IA y desarrollo.

Este proyecto prioriza calidad, simplicidad y pulido para portafolio, demostrando dominio de Hugging Face, MCP, FastAPI, Next.js y patrones agentic.

## Alcance del MVP y Funcionalidades

**MVP**:
- Grabación de audio desde navegador.
- Transcripción precisa (soporte principal español).
- Clasificación automática de transacción (ingreso/gasto, monto, categoría, fecha).
- Almacenamiento persistente de transacciones.
- Consultas por voz para resúmenes y balances.
- Respuestas generadas por voz (TTS).
- Interfaz web visual de respaldo (historial y gráficos simples).
- Confirmaciones y manejo básico de errores por voz.

**Fuera de MVP** (ver sección Mejoras Futuras): autenticación multiusuario, exportación, integraciones bancarias avanzadas.

## Arquitectura General y Flujo de la Aplicación

**Arquitectura**:
- **Cliente**: Next.js (frontend) maneja UI, grabación/reproducción de audio y comunicación con backend.
- **Backend**: FastAPI expone API REST + endpoints para streaming de audio. Orquesta STT, LLM, DB y TTS.
- **Capa de IA**: Hugging Face Inference para Whisper (STT), LLM y TTS.
- **Persistencia**: SQLite (fácil de empezar, escalable a Postgres).
- **Opcional**: MCP Server para exponer tools (cálculos, consultas estructuradas).

**Flujo principal**:
1. Usuario presiona "Hablar" → navegador graba audio (MediaRecorder) → envía blob a `/voice-input` o `/voice-query`.
2. Backend: Whisper → transcripción → LLM (parsing o respuesta) → DB (si es transacción) → LLM (respuesta natural) → TTS → devuelve audio + texto.
3. Frontend reproduce audio y actualiza UI.

**Decisiones de arquitectura clave**:
- Uso de SQLite inicial para velocidad de desarrollo (sin servidor externo).
- Prompts estructurados al LLM para outputs JSON confiables (evita parsing frágil).
- Streaming donde sea posible para mejor UX de voz.
- Separación clara: servicios reutilizables (stt_service, llm_service, tts_service, finance_service).

## Stack Tecnológico y Justificación

- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui. Justificación: Rápido, server-side rendering opcional, excelente soporte para audio Web APIs y deploy en Vercel.
- **Backend**: FastAPI (Python). Justificación: Async nativo, excelente para IA, auto-documentación OpenAPI, integración fluida con Hugging Face.
- **IA**:
  - Hugging Face InferenceClient / Inference API: Whisper-large-v3 para STT multilingüe, modelo LLM (e.g. Qwen2 o similar open), TTS (MMS o compatible).
  - MCP (Model Context Protocol): Para exponer tools financieros de forma estandarizada (futuro-proof y skill diferenciadora).
- **DB**: SQLite + SQLModel. Justificación: Cero configuración inicial, queries simples para agregaciones.
- **Audio**: Browser MediaRecorder + Web Audio API.
- **Otras**: Pydantic v2, python-dotenv, httpx, Recharts (frontend charts), yfinance o similar (API externa opcional para contexto).

## Estructura Recomendada del Proyecto

```
vozinanzas/
├── frontend/                  # Next.js
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
├── backend/                   # FastAPI
│   ├── app/
│   │   ├── api/               # routers: voice.py, transactions.py, summary.py
│   │   ├── core/              # config, deps
│   │   ├── models/            # Pydantic + SQLModel
│   │   ├── schemas/
│   │   ├── services/          # stt.py, llm.py, tts.py, finance.py
│   │   ├── db/                # session, models
│   │   └── utils/
│   ├── main.py
│   └── requirements.txt
├── mcp-server/                # Opcional: servidor MCP separado
├── docker-compose.yml
├── .env.example
├── README.md
└── implementation-plan.md
```

## Integración de Hugging Face, MCP y APIs Externas

**Hugging Face**:
- `InferenceClient` para todas las tareas.
- Whisper: `client.audio.speech_to_text(...)` o task específica.
- LLM: chat completions con structured output (JSON mode para transacciones).
- TTS: `client.text_to_speech(...)`.
- Token: Usa HF token en .env (pro tier recomendado para límites).

**MCP**:
- Implementar un MCP Server simple que exponga tools como `record_transaction`, `get_balance`, `get_monthly_summary`.
- Usar SDK oficial. Conectar desde Claude/Cursor o el propio agente.

**API Externa**:
- Opcional: Alpha Vantage / yfinance para precios de acciones o conversión de divisas (wrapper en finance_service).

## Roadmap de Desarrollo (Fases y Prioridades)

**Fase 0: Setup (P0)**
- Inicializar monorepo, Docker, .env.

**Fase 1: Core IA y Backend (P0)**
- STT + TTS + LLM básico.
- Persistencia de transacciones.

**Fase 2: Flujo de Voz Completo (P0)**
- Endpoints voice-input y voice-query.
- Frontend audio.

**Fase 3: UI y Pulido (P1)**
- Historial, gráficos, confirmaciones.

**Fase 4: MCP y Deploy (P1)**
- MCP opcional + producción.

**P2**: Tests avanzados, mejoras.

## Backlog de Tareas Técnicas (Orden Recomendado)

1. Crear estructura de carpetas y Docker Compose.
2. Configurar FastAPI con routers básicos y health check.
3. Implementar servicio STT (Whisper) + prueba con archivos de audio.
4. Implementar servicio TTS + endpoint de prueba.
5. Implementar servicio LLM para parsing de transacciones (prompt + JSON output).
6. Definir modelos DB (Transaction) y CRUD con SQLModel.
7. Endpoint `/voice-input`: audio → STT → LLM parse → save → TTS confirm.
8. Endpoint `/voice-query`: audio → STT → LLM response → TTS.
9. Frontend: grabación, envío de audio (FormData), reproducción.
10. UI: historial de transacciones y resúmenes visuales.
11. Agregaciones (mensuales, por categoría).
12. Manejo de errores y prompts robustos.
13. Integrar MCP Server básico.
14. Tests unitarios e integración.
15. Deploy y documentación final.

## Buenas Prácticas de Desarrollo, Seguridad, Manejo de Errores y Observabilidad

- **Desarrollo**: Type hints estrictos, black/ruff, pre-commit. Separar concerns (services).
- **Seguridad**: Validar todos los inputs. No almacenar audio crudo largo plazo. Usar CORS restrictivo. Keys en .env (nunca commit). Rate limiting en FastAPI.
- **Errores**: Custom exceptions + global handler en FastAPI. Mensajes de voz amigables ("No entendí el monto, ¿puedes repetirlo?").
- **Observabilidad**: Logging estructurado (loguru). Opcional: Prometheus o simple console para latencia de IA.
- **Prompts**: Versionar prompts en archivos o constants. Usar few-shot examples.

## Estrategia de Pruebas

- **Unitarias**: pytest para services (STT mock, LLM parsing, cálculos financieros).
- **Integración**: Tests de endpoints con TestClient (audio mock con archivos WAV).
- **Manuales/E2E**: Grabar audios reales en diferentes acentos/ruido. Verificar precisión STT/LLM y flujo completo.
- Métricas objetivo: >85% precisión en parsing de transacciones comunes.

## Estrategia de Despliegue y Configuración para Producción

- **Local**: `docker-compose up` (frontend + backend + db).
- **Producción**:
  - Frontend: Vercel (con environment variables).
  - Backend: Railway / Render / Fly.io (Python support, persistent disk para SQLite o Postgres).
  - Variables: `HUGGINGFACE_TOKEN`, `DATABASE_URL`, etc.
- HTTPS obligatorio. Configurar worker para background tasks si se necesitan.
- Backup simple de DB (script cron o manual).

## Posibles Mejoras Futuras (Fuera del MVP)

- Autenticación y multiusuario (Clerk / Supabase Auth).
- Exportación a CSV/PDF.
- Integración MCP avanzada con herramientas externas.
- Análisis predictivo de gastos.
- Soporte offline (service worker + modelo local pequeño).
- Notificaciones push o email.
- Dashboard analytics más rico.
- Fine-tuning de modelo Whisper/LLM para dominio financiero.

Este plan proporciona una hoja de ruta completa y sin vacíos técnicos. Seguir el orden del backlog asegura un MVP funcional rápido. Actualizar este documento según decisiones tomadas durante el desarrollo.