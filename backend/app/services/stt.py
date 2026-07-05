from functools import lru_cache

from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError, InferenceTimeoutError

from app.core.config import get_settings
from app.core.exceptions import TranscriptionError


class SttService:
    """Transcribe audio a texto usando un modelo ASR vía Hugging Face Inference."""

    def __init__(self, client: InferenceClient) -> None:
        self._client = client

    def transcribe(self, audio: bytes) -> str:
        try:
            output = self._client.automatic_speech_recognition(audio)
        except InferenceTimeoutError as exc:
            raise TranscriptionError("El servicio de transcripción no respondió a tiempo") from exc
        except HfHubHTTPError as exc:
            raise TranscriptionError("No se pudo procesar el audio con el servicio de transcripción") from exc

        text = output.text.strip()
        if not text:
            raise TranscriptionError("No se detectó voz en el audio")
        return text


@lru_cache
def get_stt_service() -> SttService:
    settings = get_settings()
    client = InferenceClient(model=settings.hf_stt_model, token=settings.huggingface_token or None)
    return SttService(client)