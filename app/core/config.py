from __future__ import annotations

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field("SupportOps AI Backend", validation_alias="APP_NAME")
    env: str = Field("development", validation_alias="ENV")
    debug: bool = Field(False, validation_alias="DEBUG")

    database_url: str = Field(
        "postgresql+psycopg://postgres:postgres@localhost:5432/supportops",
        validation_alias="DATABASE_URL",
    )
    redis_url: str = Field("redis://localhost:6379/0", validation_alias="REDIS_URL")

    jwt_secret: str = Field("change-me", validation_alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(14, validation_alias="REFRESH_TOKEN_EXPIRE_DAYS")

    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", validation_alias="OPENAI_MODEL")
    ai_timeout_seconds: int = Field(12, validation_alias="AI_TIMEOUT_SECONDS")

    rq_job_timeout: int = Field(300, validation_alias="RQ_JOB_TIMEOUT")
    rq_async: bool = Field(True, validation_alias="RQ_ASYNC")

    testing: bool = Field(False, validation_alias="TESTING")
    log_level: str = Field("INFO", validation_alias="LOG_LEVEL")


settings = Settings()
