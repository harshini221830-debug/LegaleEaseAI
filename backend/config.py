from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = Field(
        default="LegalEase",
        validation_alias="APP_NAME"
    )

    gemini_api_key: str = Field(
        default="",
        validation_alias="GEMINI_API_KEY"
    )

    gemini_model: str = Field(
        default="gemini-3.8-flash",
        validation_alias="GEMINI_MODEL"
    )

    demo_mode: bool = Field(
        default=True,
        validation_alias="DEMO_MODE"
    )

    backend_url: str = Field(
        default="http://127.0.0.1:8000",
        validation_alias="BACKEND_URL"
    )

    allowed_origins: str = Field(
        default="http://localhost:8501,http://127.0.0.1:8501",
        validation_alias="ALLOWED_ORIGINS"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()