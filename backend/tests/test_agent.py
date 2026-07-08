from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from groq import RateLimitError


def test_agent_chat_happy_path(client: TestClient) -> None:
    with patch("app.api.agent.run_agent", new=AsyncMock(return_value="Tu balance neto es 800.00.")):
        response = client.post("/agent/chat", json={"message": "cuál es mi balance"})

    assert response.status_code == 200
    assert response.json() == {"reply": "Tu balance neto es 800.00."}


def test_agent_chat_timeout(client: TestClient) -> None:
    with patch("app.api.agent.run_agent", new=AsyncMock(side_effect=TimeoutError())):
        response = client.post("/agent/chat", json={"message": "hola"})

    assert response.status_code == 504


def test_agent_chat_rate_limit(client: TestClient) -> None:
    fake_response = AsyncMock()
    fake_response.status_code = 429
    error = RateLimitError("rate limited", response=fake_response, body=None)

    with patch("app.api.agent.run_agent", new=AsyncMock(side_effect=error)):
        response = client.post("/agent/chat", json={"message": "hola"})

    assert response.status_code == 429


def test_agent_chat_mensaje_vacio(client: TestClient) -> None:
    response = client.post("/agent/chat", json={"message": ""})
    assert response.status_code == 422