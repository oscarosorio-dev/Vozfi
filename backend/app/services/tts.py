import httpx

from app.core.config import get_settings
from app.core.exceptions import SynthesisError

_ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


class TtsService:
    """Convierte texto a audio usando la API de ElevenLabs."""

    def __init__(self, api_key: str, voice_id: str, model_id: str) -> None:
        self._api_key = api_key
        self._voice_id = voice_id
        self._model_id = model_id

    def synthesize(self, text: str) -> tuple[bytes, str]:
        """Retorna (audio_bytes, content_type). ElevenLabs devuelve MP3 por defecto."""
        headers = {"xi-api-key": self._api_key, "Content-Type": "application/json"}
        payload = {"text": text, "model_id": self._model_id}
        url = _ELEVENLABS_TTS_URL.format(voice_id=self._voice_id)

        try:
            response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise SynthesisError("El servicio de síntesis de voz no respondió a tiempo") from exc
        except httpx.HTTPStatusError as exc:
            raise SynthesisError(f"No se pudo generar el audio de respuesta: {exc.response.text}") from exc

        return response.content, "audio/mpeg"


def get_tts_service() -> TtsService:
    settings = get_settings()
    return TtsService(
        api_key=settings.elevenlabs_api_key,
        voice_id=settings.elevenlabs_voice_id,
        model_id=settings.elevenlabs_model_id,
    )