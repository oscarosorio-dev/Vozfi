from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.exceptions import TranscriptionError
from app.services.stt import SttService, get_stt_service

router = APIRouter(prefix="/voice", tags=["voice"])

ALLOWED_CONTENT_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp4",
    "audio/webm",
    "audio/ogg",
    "audio/flac",
}


class TranscriptionResult(BaseModel):
    text: str


@router.post("/transcribe", response_model=TranscriptionResult)
async def transcribe_audio(
    file: UploadFile,
    stt_service: SttService = Depends(get_stt_service),
) -> TranscriptionResult:
    settings = get_settings()

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Formato de audio no soportado: {file.content_type}",
        )

    audio_bytes = await file.read()
    max_size = settings.max_audio_size_mb * 1024 * 1024
    if len(audio_bytes) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"El audio excede el tamaño máximo de {settings.max_audio_size_mb}MB",
        )
    if not audio_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archivo de audio vacío")

    try:
        text = stt_service.transcribe(audio_bytes)
    except TranscriptionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return TranscriptionResult(text=text)