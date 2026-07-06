from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph.state import CompiledStateGraph

from app.agent.state import AgentState
from app.core.config import get_settings

_SYSTEM_PROMPT = (
    "Eres el asistente financiero de Vozfi. Ayudas a registrar transacciones (ingresos y "
    "gastos) y a consultar el balance del usuario, usando exclusivamente las herramientas "
    "disponibles. Cada mensaje es una solicitud independiente, sin memoria de turnos previos.\n\n"
    "REGLA ESTRICTA: llama como máximo UNA herramienta en total por mensaje del usuario. "
    "En cuanto recibas el resultado de esa herramienta, tu siguiente respuesta DEBE ser texto "
    "final para el usuario, sin ninguna llamada adicional a herramientas (ni de verificación, "
    "ni de consulta, ni de ningún tipo). No verifiques ni confirmes resultados llamando otra "
    "herramienta.\n\n"
    "Si registras una transacción, confirma con el monto y la categoría exactos, sin consultar "
    "balance ni resumen después. No hagas preguntas de seguimiento ni ofrezcas continuar la "
    "conversación. Responde siempre en español, en una sola frase breve y directa."
)

_agent: CompiledStateGraph | None = None


async def get_agent() -> CompiledStateGraph:
    """
    Retorna el agente compilado (singleton de proceso).

    Se conecta al mcp-server vía streamable-http para obtener sus herramientas
    (registrar transacciones, consultar balance y resumen por categoría) y usa
    Groq como LLM con soporte de tool-calling.
    """
    global _agent
    if _agent is not None:
        return _agent

    settings = get_settings()
    client = MultiServerMCPClient(
        {
            "vozfi": {
                "url": settings.mcp_server_url,
                "transport": "streamable_http",
            }
        }
    )
    tools = await client.get_tools()
    model = ChatGroq(model=settings.groq_llm_model, api_key=settings.groq_api_key)

    _agent = create_agent(
        model,
        tools,
        system_prompt=_SYSTEM_PROMPT,
        state_schema=AgentState,
        middleware=[ToolCallLimitMiddleware(run_limit=1, exit_behavior="end")],
    )
    return _agent