import base64
import logging

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import ParsingError, QueryAnsweringError, SynthesisError, TranscriptionError
from app.db.repositories.transaction import TransactionRepository
from app.db.session import get_db
from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionRead
from app.services.llm import LlmParsingService, LlmQueryService, get_llm_query_service, get_llm_service
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


def _build_confirmation_message(transaction: Transaction) -> str:
    """Genera el mensaje de confirmación en español que se envía al servicio TTS."""
    verb = "ingreso" if transaction.type == TransactionType.INCOME else "gasto"
    return f"Registré un {verb} de {transaction.amount:.2f} en {transaction.category}."


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


class ParseRequest(BaseModel):
    transcript: str = Field(min_length=1)


@router.post("/parse", response_model=TransactionCreate)
async def parse_transaction(
    payload: ParseRequest,
    llm_service: LlmParsingService = Depends(get_llm_service),
) -> TransactionCreate:
    """Extrae una transacción estructurada de un texto. Endpoint de prueba aislado del flujo completo."""
    try:
        return llm_service.parse_transaction(payload.transcript)
    except ParsingError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


class VoiceInputResponse(BaseModel):
    transcript: str
    transaction: TransactionRead
    confirmation_text: str
    audio_base64: str | None = None
    audio_content_type: str | None = None


@router.post("/voice-input", response_model=VoiceInputResponse, status_code=status.HTTP_201_CREATED)
async def voice_input(
    file: UploadFile,
    stt_service: SttService = Depends(get_stt_service),
    llm_service: LlmParsingService = Depends(get_llm_service),
    tts_service: TtsService = Depends(get_tts_service),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> VoiceInputResponse:
    """
    Flujo completo de registro de una transacción por voz.

    Orquesta: validación de audio -> STT (transcripción) -> LLM (extracción
    estructurada) -> persistencia -> TTS (confirmación hablada).

    La síntesis de voz es best-effort: si el TTS falla, la transacción ya
    persistida se devuelve igual, con `audio_base64` en None.
    """
    audio_bytes = await _read_validated_audio(file, settings)

    try:
        transcript = stt_service.transcribe(audio_bytes, file.content_type)
    except TranscriptionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    try:
        parsed = llm_service.parse_transaction(transcript)
    except ParsingError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    transaction = TransactionRepository(db).create(parsed)
    confirmation_text = _build_confirmation_message(transaction)

    audio_base64: str | None = None
    audio_content_type: str | None = None
    try:
        confirmation_audio, audio_content_type = tts_service.synthesize(confirmation_text)
        audio_base64 = base64.b64encode(confirmation_audio).decode("ascii")
    except SynthesisError as exc:
        logger.warning("TTS falló en voice-input, se retorna sin audio: %s", exc)
        audio_base64 = None
        audio_content_type = None

    return VoiceInputResponse(
        transcript=transcript,
        transaction=TransactionRead.model_validate(transaction),
        confirmation_text=confirmation_text,
        audio_base64=audio_base64,
        audio_content_type=audio_content_type,
    )


class VoiceQueryResponse(BaseModel):
    transcript: str
    answer_text: str
    audio_base64: str | None = None
    audio_content_type: str | None = None


@router.post("/voice-query", response_model=VoiceQueryResponse)
async def voice_query(
    file: UploadFile,
    stt_service: SttService = Depends(get_stt_service),
    query_service: LlmQueryService = Depends(get_llm_query_service),
    tts_service: TtsService = Depends(get_tts_service),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> VoiceQueryResponse:
    """
    Flujo de consulta financiera por voz.

    Orquesta: validación de audio -> STT (transcripción) -> cálculo de balance y
    resumen por categoría -> LLM (respuesta en lenguaje natural) -> TTS (respuesta hablada).

    La síntesis de voz es best-effort: si el TTS falla, `answer_text` se devuelve
    igual con `audio_base64` en None.
    """
    audio_bytes = await _read_validated_audio(file, settings)

    try:
        transcript = stt_service.transcribe(audio_bytes, file.content_type)
    except TranscriptionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    repository = TransactionRepository(db)
    financial_context = {
        "balance": repository.get_balance(),
        "resumen_por_categoria": repository.get_summary_by_category(),
    }

    try:
        answer_text = query_service.answer_query(transcript, financial_context)
    except QueryAnsweringError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    audio_base64: str | None = None
    audio_content_type: str | None = None
    try:
        answer_audio, audio_content_type = tts_service.synthesize(answer_text)
        audio_base64 = base64.b64encode(answer_audio).decode("ascii")
    except SynthesisError as exc:
        logger.warning("TTS falló en voice-query, se retorna sin audio: %s", exc)
        audio_base64 = None
        audio_content_type = None

    return VoiceQueryResponse(
        transcript=transcript,
        answer_text=answer_text,
        audio_base64=audio_base64,
        audio_content_type=audio_content_type,
    )

class VoiceAgentResponse(BaseModel):
    transcript: str
    answer_text: str
    audio_base64: str | None = None
    audio_content_type: str | None = None

@router.post("/voice-agent", response_model=VoiceAgentResponse)
async def voice_agent(
    file: UploadFile,
    stt_service: SttService = Depends(get_stt_service),
    tts_service: TtsService = Depends(get_tts_service),
    settings: Settings = Depends(get_settings),
) -> VoiceAgentResponse:
    """
    Procesa una consulta o comando financiero por voz de manera completamente agente.

    Orquesta: Validación de audio -> STT -> LangGraph Agent (que invoca herramientas de MCP)
    -> TTS para sintetizar la respuesta hablada.
    """
    audio_bytes = await _read_validated_audio(file, settings)

    try:
        transcript = stt_service.transcribe(audio_bytes, file.content_type)
    except TranscriptionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    try:
        from app.agent.graph import run_agent
        answer_text = await run_agent(transcript)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    audio_base64: str | None = None
    audio_content_type: str | None = None
    try:
        answer_audio, audio_content_type = tts_service.synthesize(answer_text)
        audio_base64 = base64.b64encode(answer_audio).decode("ascii")
    except SynthesisError as exc:
        logger.warning("TTS falló en voice-agent, se retorna sin audio: %s", exc)
        audio_base64 = None
        audio_content_type = None

    return VoiceAgentResponse(
        transcript=transcript,
        answer_text=answer_text,
        audio_base64=audio_base64,
        audio_content_type=audio_content_type,
    )