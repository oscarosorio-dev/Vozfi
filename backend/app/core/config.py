from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Vozfi API"
    environment: str = "development"
    debug: bool = False

    cors_origins: list[str] = ["http://localhost:3000"]

    huggingface_token: str = ""
    hf_provider: str = "auto"
    groq_api_key: str = ""
    groq_llm_model: str = "llama-3.1-8b-instant"
    groq_stt_model: str = "whisper-large-v3-turbo"
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "t4TEtgvmo5ooLNFCHPxx"
    elevenlabs_model_id: str = "eleven_multilingual_v2"
    hf_llm_model: str = "Qwen/Qwen2.5-7B-Instruct"
    max_audio_size_mb: int = 10
    max_tts_text_length: int = 500

    mcp_server_url: str = "http://mcp-server:8100/mcp"

    database_url: str = "postgresql+psycopg://vozfi:vozfi@postgres:5432/vozfi"


@lru_cache
def get_settings() -> Settings:
    return Settings()