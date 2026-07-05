# Vozfi

**Vozfi** es un asistente personal de finanzas impulsado por voz que permite registrar ingresos y gastos mediante comandos de voz naturales y obtener resúmenes, balances y detalles mediante consultas habladas.

## Estructura del Proyecto

La arquitectura se basa en una separación de responsabilidades entre frontend, backend y servicios de IA para facilitar el mantenimiento, la escalabilidad y la reutilización del código. Asimismo, la estructura de carpetas organiza cada módulo de forma independiente, haciendo el proyecto más claro y sencillo de extender.

```
vozinanzas/
├── frontend/                  # Next.js
├── backend/                   # FastAPI
├── mcp-server/                # Servidor MCP
├── docker-compose.yml         # Contenedores
├── .env.example               # Variables de Entorno
└── README.md                  
```