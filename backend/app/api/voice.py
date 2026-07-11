import base64
import logging

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status
from pydantic import BaseModel, Field

from app.agent.service import run_agent
from app.core.config import Settings, get_settings
from app.core.exceptions import SynthesisError, TranscriptionError
from app.core.http_errors import raise_friendly_http_error
from app.services.stt import SttService, get_stt_service
from app.services.tts import TtsService, get_tts_service

router = APIRouter(prefix="/voice", tags=["voice"])
logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp4",
    "audio/webm",
    "audio/ogg",
    "audio/flac",
}


async def _read_validated_audio(file: UploadFile, settings: Settings) -> bytes:
    """
    Valida el content-type y tamaño del audio recibido y retorna sus bytes.

    Lanza HTTPException 415 (formato no soportado), 400 (vacío) o 413 (excede
    `settings.max_audio_size_mb`) según corresponda.
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Formato de audio no soportado: {file.content_type}",
        )

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archivo de audio vacío")

    max_size = settings.max_audio_size_mb * 1024 * 1024
    if len(audio_bytes) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"El audio excede el tamaño máximo de {settings.max_audio_size_mb}MB",
        )

    return audio_bytes


class TranscriptionResult(BaseModel):
    text: str


@router.post("/transcribe", response_model=TranscriptionResult)
async def transcribe_audio(
    file: UploadFile,
    stt_service: SttService = Depends(get_stt_service),
    settings: Settings = Depends(get_settings),
) -> TranscriptionResult:
    """Transcribe un archivo de audio a texto. Endpoint de prueba aislado del flujo completo."""
    audio_bytes = await _read_validated_audio(file, settings)

    try:
        text = stt_service.transcribe(audio_bytes, file.content_type)
    except TranscriptionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return TranscriptionResult(text=text)


class SynthesisRequest(BaseModel):
    text: str = Field(min_length=1)


@router.post("/synthesize")
async def synthesize_speech(
    payload: SynthesisRequest,
    tts_service: TtsService = Depends(get_tts_service),
    settings: Settings = Depends(get_settings),
) -> Response:
    """Sintetiza texto a audio. Endpoint de prueba aislado del flujo completo."""
    if len(payload.text) > settings.max_tts_text_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El texto excede el máximo de {settings.max_tts_text_length} caracteres",
        )

    try:
        audio, content_type = tts_service.synthesize(payload.text)
    except SynthesisError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return Response(content=audio, media_type=content_type)


class VoiceInputResponse(BaseModel):
    transcript: str
    reply: str
    audio_base64: str | None = None
    audio_content_type: str | None = None


@router.post("/voice-input", response_model=VoiceInputResponse)
async def voice_input(
    file: UploadFile,
    stt_service: SttService = Depends(get_stt_service),
    tts_service: TtsService = Depends(get_tts_service),
    settings: Settings = Depends(get_settings),
) -> VoiceInputResponse:
    """
    Flujo de voz unificado: STT -> agente financiero -> TTS de la respuesta.

    El agente decide internamente (vía tool-calling contra el mcp-server) si
    debe registrar una transacción o responder una consulta de balance; este
    endpoint no conoce ni duplica esa lógica de negocio.

    La síntesis de voz es best-effort: si el TTS falla, `reply` se devuelve
    igual, con `audio_base64` en None.
    """
    audio_bytes = await _read_validated_audio(file, settings)

    try:
        transcript = stt_service.transcribe(audio_bytes, file.content_type)
    except TranscriptionError as exc:
        raise_friendly_http_error(exc, context="voice-input/stt")

    try:
        reply = await run_agent(transcript)
    except Exception as exc:
        raise_friendly_http_error(exc, context="voice-input/agent")

    audio_base64: str | None = None
    audio_content_type: str | None = None
    try:
        audio, audio_content_type = tts_service.synthesize(reply)
        audio_base64 = base64.b64encode(audio).decode("ascii")
    except SynthesisError as exc:
        logger.warning("TTS falló en voice-input, se retorna sin audio: %s", exc)
        audio_base64 = None
        audio_content_type = None

    return VoiceInputResponse(
        transcript=transcript,
        reply=reply,
        audio_base64=audio_base64,
        audio_content_type=audio_content_type,
    )