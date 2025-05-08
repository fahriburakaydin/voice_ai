import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path, override=False)

class Settings(BaseSettings):
    gcp_project: str
    gcs_bucket: str
    redis_url: str

    openai_api_key: str
    eleven_api_key: str
    pinecone_api_key: str
    pinecone_env: str
    pinecone_index: str

    # Model & voice config
    whisper_model: str = "whisper-1"
    gpt_model: str    = "gpt-4"
    embedding_model: str = "text-embedding-ada-002"
    tts_voice_id: str = "cgSgspJ2msm6clMCkdW9"
    tts_stability: float = 0.7
    tts_similarity: float = 0.75

    # Memory settings
    short_term_size: int = 8
    memory_k: int = 5

    model_config = SettingsConfigDict(

        str_strip_whitespace = True   # trims leading/trailing spaces/newlines on ALL str fields, this was causing erro in gcp
    )
settings = Settings()
