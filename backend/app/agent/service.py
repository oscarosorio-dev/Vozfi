import asyncio
import logging

from groq import BadRequestError, RateLimitError
from langchain_core.messages import HumanMessage, ToolMessage
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.agent.graph import get_agent

logger = logging.getLogger(__name__)

AGENT_TIMEOUT_SECONDS = 30
AGENT_RECURSION_LIMIT = 6


def _extract_reply(messages: list) -> str:
    """
    Retorna el texto de respuesta al usuario.

    Prioriza el contenido de la última `ToolMessage` real (texto ya redactado
    en español por nuestras propias tools) sobre el `AIMessage` final. Excluye
    los `ToolMessage` sintéticos con `status="error"` que genera
    `ToolCallLimitMiddleware` al bloquear una tool call excedente.
    """
    tool_messages = [
        m for m in messages if isinstance(m, ToolMessage) and getattr(m, "status", "success") != "error"
    ]
    if not tool_messages:
        return messages[-1].content

    content = tool_messages[-1].content
    if isinstance(content, list):
        content = " ".join(block.get("text", "") for block in content if isinstance(block, dict))
    return content


def _is_transient_tool_call_error(exc: BaseException) -> bool:
    """
    Groq a veces falla en generar el tool call en formato correcto
    (`tool_use_failed`) y responde 400; un reintento normalmente lo resuelve.
    Otros 400 (ej: payload inválido) no deben reintentarse.
    """
    if isinstance(exc, RateLimitError):
        return True
    if isinstance(exc, BadRequestError):
        body = exc.body if isinstance(exc.body, dict) else {}
        return body.get("error", {}).get("code") == "tool_use_failed"
    return False


@retry(
    retry=retry_if_exception(_is_transient_tool_call_error),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def run_agent(message: str) -> str:
    """
    Punto de entrada único del agente financiero.

    Reutilizable por cualquier canal (texto vía `/agent/chat`, voz vía
    `/voice/voice-input`, y a futuro WhatsApp/Telegram/etc.) sin duplicar
    lógica de orquestación, retry ni parsing de la respuesta.
    """
    agent = await get_agent()
    last_state: dict | None = None

    async def _run() -> None:
        nonlocal last_state
        async for step in agent.astream(
            {"messages": [HumanMessage(content=message)]},
            config={"recursion_limit": AGENT_RECURSION_LIMIT},
            stream_mode="values",
        ):
            last_state = step
            last_message = step["messages"][-1]
            logger.info(
                "agent step: type=%s content=%r tool_calls=%s",
                type(last_message).__name__,
                last_message.content,
                getattr(last_message, "tool_calls", None),
            )

    await asyncio.wait_for(_run(), timeout=AGENT_TIMEOUT_SECONDS)
    return _extract_reply(last_state["messages"])