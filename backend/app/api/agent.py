from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agent.service import run_agent
from app.core.http_errors import raise_friendly_http_error

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
    except Exception as exc:
        raise_friendly_http_error(exc, context="agent/chat")

    return AgentChatResponse(reply=reply)