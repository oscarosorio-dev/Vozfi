import json
from datetime import UTC, datetime
from functools import lru_cache

from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError, InferenceTimeoutError
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.exceptions import ParsingError, QueryAnsweringError
from app.schemas.transaction import TransactionCreate

_SYSTEM_PROMPT = (
    "Eres un asistente que extrae transacciones financieras de texto en español. "
    "Responde EXCLUSIVAMENTE con un objeto JSON (sin markdown, sin texto adicional) con las claves: "
    "type ('income' o 'expense'), amount (número positivo), category (string corta), "
    "description (string o null). Si no hay una transacción clara en el texto, responde "
    '{"error": "sin_transaccion"}.'
)

_QUERY_SYSTEM_PROMPT = (
    "Eres un asistente financiero que responde preguntas en español sobre las finanzas del usuario. "
    "Usa EXCLUSIVAMENTE los datos numéricos que te entrega el usuario en el mensaje (balance e ingresos/gastos "
    "por categoría). No inventes cifras. Responde en una o dos frases breves, en tono natural, listas para "
    "convertirse en voz."
)


class LlmParsingService:
    """Convierte una transcripción en lenguaje natural en una transacción estructurada."""

    def __init__(self, client: InferenceClient, model: str) -> None:
        self._client = client
        self._model = model

    def parse_transaction(self, transcript: str) -> TransactionCreate:
        try:
            completion = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": transcript},
                ],
                temperature=0,
            )
        except InferenceTimeoutError as exc:
            raise ParsingError("El servicio de interpretación no respondió a tiempo") from exc
        except HfHubHTTPError as exc:
            raise ParsingError(f"No se pudo interpretar la transacción: {exc}") from exc

        content = completion.choices[0].message.content or ""
        data = self._extract_json(content)

        if "error" in data:
            raise ParsingError("No se identificó una transacción en el audio")

        data.setdefault("occurred_at", datetime.now(UTC).isoformat())

        try:
            return TransactionCreate.model_validate(data)
        except ValidationError as exc:
            raise ParsingError("La transcripción no contiene una transacción válida") from exc

    @staticmethod
    def _extract_json(content: str) -> dict:
        content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise ParsingError("La respuesta del modelo no es JSON válido") from exc


class LlmQueryService:
    """Responde preguntas en lenguaje natural sobre el estado financiero del usuario."""

    def __init__(self, client: InferenceClient, model: str) -> None:
        self._client = client
        self._model = model

    def answer_query(self, transcript: str, financial_context: dict) -> str:
        """
        Genera una respuesta hablable a partir de la pregunta del usuario y los
        datos financieros ya calculados (balance y resumen por categoría).
        """
        user_message = (
            f"Pregunta: {transcript}\n"
            f"Datos disponibles (JSON): {json.dumps(financial_context, ensure_ascii=False)}"
        )
        try:
            completion = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": _QUERY_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0,
            )
        except InferenceTimeoutError as exc:
            raise QueryAnsweringError("El servicio de interpretación no respondió a tiempo") from exc
        except HfHubHTTPError as exc:
            raise QueryAnsweringError(f"No se pudo generar una respuesta a la consulta: {exc}") from exc

        answer = (completion.choices[0].message.content or "").strip()
        if not answer:
            raise QueryAnsweringError("El modelo no generó una respuesta")
        return answer


def _build_inference_client() -> InferenceClient:
    settings = get_settings()
    return InferenceClient(provider=settings.hf_provider, token=settings.huggingface_token or None)


@lru_cache
def get_llm_service() -> LlmParsingService:
    settings = get_settings()
    return LlmParsingService(_build_inference_client(), settings.hf_llm_model)


@lru_cache
def get_llm_query_service() -> LlmQueryService:
    settings = get_settings()
    return LlmQueryService(_build_inference_client(), settings.hf_llm_model)