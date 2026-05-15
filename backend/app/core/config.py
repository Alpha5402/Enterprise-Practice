"""Application configuration loaded from environment variables."""

import json
from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Competitive Intelligence API"
    app_version: str = "0.1.0"
    app_env: str = "local"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = Field(
        default="postgresql+psycopg://competitive_intel:competitive_intel@localhost:5432/competitive_intel"
    )
    backend_cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )
    redis_url: str = "redis://localhost:6379/0"
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"
    embedding_model: str = "chroma-default"
    rag_collection_name: str = "competitive_intelligence"
    rag_chunk_size: int = 1200
    rag_chunk_overlap: int = 180

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        """Parse comma-separated CORS origins from environment variables."""
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                decoded = json.loads(stripped)
                if isinstance(decoded, list):
                    return [str(origin).strip() for origin in decoded if str(origin).strip()]
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached settings for dependency injection."""
    return Settings()


settings = get_settings()
