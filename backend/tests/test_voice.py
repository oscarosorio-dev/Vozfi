from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.core.exceptions import SynthesisError, TranscriptionError
from app.services.stt import get_stt_service
from app.services.tts import get_tts_service


class _FakeStt:
    def transcribe(self, audio: bytes, content_type: str) -> str:
        return "gasté 20 mil en comida"


class _FakeSttFail:
    def transcribe(self, audio: bytes, content_type: str) -> str:
        raise TranscriptionError("no se detectó voz")


class _FakeTts:
    def synthesize(self, text: str) -> tuple[bytes, str]:
        return b"FAKE_AUDIO", "audio/mpeg"


class _FakeTtsFail:
    def synthesize(self, text: str) -> tuple[bytes, str]:
        raise SynthesisError("proveedor caído")


def test_voice_input_happy_path(client: TestClient) -> None:
    client.app.dependency_overrides[get_stt_service] = lambda: _FakeStt()
    client.app.dependency_overrides[get_tts_service] = lambda: _FakeTts()

    with patch("app.api.voice.run_agent", new=AsyncMock(return_value="Registrado un gasto de 20000.00 en comida.")):
        response = client.post("/voice/voice-input", files={"file": ("a.wav", b"RIFFxxxx", "audio/wav")})

    assert response.status_code == 200
    data = response.json()
    assert data["transcript"] == "gasté 20 mil en comida"
    assert data["reply"] == "Registrado un gasto de 20000.00 en comida."
    assert data["audio_base64"] is not None
    assert data["audio_content_type"] == "audio/mpeg"


def test_voice_input_tts_falla_best_effort(client: TestClient) -> None:
    client.app.dependency_overrides[get_stt_service] = lambda: _FakeStt()
    client.app.dependency_overrides[get_tts_service] = lambda: _FakeTtsFail()

    with patch("app.api.voice.run_agent", new=AsyncMock(return_value="Registrado.")):
        response = client.post("/voice/voice-input", files={"file": ("a.wav", b"RIFFxxxx", "audio/wav")})

    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Registrado."
    assert data["audio_base64"] is None


def test_voice_input_stt_falla(client: TestClient) -> None:
    client.app.dependency_overrides[get_stt_service] = lambda: _FakeSttFail()

    response = client.post("/voice/voice-input", files={"file": ("a.wav", b"RIFFxxxx", "audio/wav")})
    assert response.status_code == 502
    assert response.json()["detail"] == "No entendí lo que dijiste, ¿puedes repetirlo?"


def test_voice_input_content_type_no_soportado(client: TestClient) -> None:
    response = client.post("/voice/voice-input", files={"file": ("a.txt", b"hola", "text/plain")})
    assert response.status_code == 415


def test_voice_input_archivo_vacio(client: TestClient) -> None:
    response = client.post("/voice/voice-input", files={"file": ("a.wav", b"", "audio/wav")})
    assert response.status_code == 400


def test_voice_input_excede_tamano_maximo(client: TestClient) -> None:
    big_audio = b"0" * (11 * 1024 * 1024)
    response = client.post("/voice/voice-input", files={"file": ("a.wav", big_audio, "audio/wav")})
    assert response.status_code == 413