import logging
from typing import NoReturn

from fastapi import HTTPException, status
from groq import RateLimitError

from app.core.exceptions import TranscriptionError

logger = logging.getLogger(__name__)


def raise_friendly_http_error(exc: Exception, *, context: str) -> NoReturn:
    """
    Convierte una excepción interna en un `HTTPException` con un mensaje
    amigable en español, apto para leerse en voz alta.

    El detalle técnico original se loguea server-side (para debugging) pero
    nunca se expone al cliente, evitando filtrar errores internos de
    proveedores externos (Groq, ElevenLabs, etc.).
    """
    logger.error("%s: %s", context, exc, exc_info=exc)

    if isinstance(exc, TranscriptionError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No entendí lo que dijiste, ¿puedes repetirlo?",
        ) from exc
    if isinstance(exc, TimeoutError):
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Estoy tardando más de lo normal, intenta de nuevo en un momento.",
        ) from exc
    if isinstance(exc, RateLimitError):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Estoy recibiendo muchas solicitudes ahora mismo, espera unos segundos e intenta de nuevo.",
        ) from exc

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="No pude procesar tu solicitud, ¿puedes intentarlo de nuevo?",
    ) from exc