import httpx

from app.core.config import get_settings
from app.core.exceptions import TranscriptionError

_GROQ_TRANSCRIPTIONS_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


class SttService:
    """Transcribe audio a texto usando la API de Groq (Whisper)."""

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def transcribe(self, audio: bytes, content_type: str) -> str:
        """Transcribe audio a texto. `content_type` se usa para nombrar el archivo enviado."""
        extension = content_type.split("/")[-1].split(";")[0] or "wav"
        files = {"file": (f"audio.{extension}", audio, content_type)}
        data = {"model": self._model}
        headers = {"Authorization": f"Bearer {self._api_key}"}

        try:
            response = httpx.post(
                _GROQ_TRANSCRIPTIONS_URL,
                headers=headers,
                data=data,
                files=files,
                timeout=30.0,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise TranscriptionError("El servicio de transcripción no respondió a tiempo") from exc
        except httpx.HTTPStatusError as exc:
            raise TranscriptionError(f"No se pudo procesar el audio: {exc.response.text}") from exc

        text = response.json().get("text", "").strip()
        if not text:
            raise TranscriptionError("No se detectó voz en el audio")
        return text


def get_stt_service() -> SttService:
    settings = get_settings()
    return SttService(api_key=settings.groq_api_key, model=settings.groq_stt_model)