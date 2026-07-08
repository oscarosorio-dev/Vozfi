from fastapi import APIRouter, HTTPException, status
from groq import RateLimitError
from pydantic import BaseModel, Field

from app.agent.service import run_agent

router = APIRouter(prefix="/agent", tags=["agent"])


class AgentChatRequest(BaseModel):
    message: str = Field(min_length=1)


class AgentChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=AgentChatResponse)
async def chat_with_agent(payload: AgentChatRequest) -> AgentChatResponse:
    """Envía un mensaje de texto al agente financiero (canal texto)."""
    try:
        reply = await run_agent(payload.message)
    except TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="El agente no respondió a tiempo",
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