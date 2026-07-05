from functools import lru_cache

from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError, InferenceTimeoutError

from app.core.config import get_settings
from app.core.exceptions import SynthesisError


class TtsService:
    """Convierte texto a audio usando un modelo TTS vía Hugging Face Inference."""

    def __init__(self, client: InferenceClient) -> None:
        self._client = client

    def synthesize(self, text: str) -> bytes:
        try:
            return self._client.text_to_speech(text)
        except InferenceTimeoutError as exc:
            raise SynthesisError("El servicio de síntesis de voz no respondió a tiempo") from exc
        except HfHubHTTPError as exc:
            raise SynthesisError("No se pudo generar el audio de respuesta") from exc


@lru_cache
def get_tts_service() -> TtsService:
    settings = get_settings()
    client = InferenceClient(model=settings.hf_tts_model, token=settings.huggingface_token or None)
    return TtsService(client)