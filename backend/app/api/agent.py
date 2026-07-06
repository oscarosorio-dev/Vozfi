import asyncio
import logging

from groq import RateLimitError
from fastapi import APIRouter, HTTPException, status
from langchain_core.messages import HumanMessage, ToolMessage
from pydantic import BaseModel, Field
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.agent.graph import get_agent

router = APIRouter(prefix="/agent", tags=["agent"])
logger = logging.getLogger(__name__)

_AGENT_TIMEOUT_SECONDS = 30
_AGENT_RECURSION_LIMIT = 6


class AgentChatRequest(BaseModel):
    message: str = Field(min_length=1)


class AgentChatResponse(BaseModel):
    reply: str


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


@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def _invoke_agent(message: str) -> str:
    agent = await get_agent()
    last_state: dict | None = None

    async def _run() -> None:
        nonlocal last_state
        async for step in agent.astream(
            {"messages": [HumanMessage(content=message)]},
            config={"recursion_limit": _AGENT_RECURSION_LIMIT},
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

    await asyncio.wait_for(_run(), timeout=_AGENT_TIMEOUT_SECONDS)
    return _extract_reply(last_state["messages"])


@router.post("/chat", response_model=AgentChatResponse)
async def chat_with_agent(payload: AgentChatRequest) -> AgentChatResponse:
    """Envía un mensaje al agente financiero (LangGraph + herramientas del mcp-server)."""
    try:
        reply = await _invoke_agent(payload.message)
    except TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"El agente no respondió en {_AGENT_TIMEOUT_SECONDS}s",
        ) from exc
    except RateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Límite de peticiones de Groq alcanzado, intenta en unos segundos",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"El agente no pudo procesar el mensaje: {exc}",
        ) from exc

    return AgentChatResponse(reply=reply)