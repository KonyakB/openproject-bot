from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    app_name: str = Field(default="openproject-discord-assistant", alias="APP_NAME")
    app_base_url: str = Field(default="http://localhost:8000", alias="APP_BASE_URL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    discord_public_key: str = Field(alias="DISCORD_PUBLIC_KEY")
    discord_application_id: str = Field(alias="DISCORD_APPLICATION_ID")
    discord_bot_token: str = Field(alias="DISCORD_BOT_TOKEN")

    openproject_base_url: str = Field(alias="OPENPROJECT_BASE_URL")
    openproject_api_token: str = Field(alias="OPENPROJECT_API_TOKEN")

    llm_api_key: str = Field(alias="LLM_API_KEY")
    llm_base_url: str = Field(default="https://api.openai.com/v1", alias="LLM_BASE_URL")
    llm_model: str = Field(default="gpt-4.1-mini", alias="LLM_MODEL")

    database_url: str = Field(alias="DATABASE_URL")

    auto_create_confidence_threshold: float = 0.85


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
