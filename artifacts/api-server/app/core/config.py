from functools import lru_cache
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="QuizIt API", validation_alias="APP_NAME")
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")

    # Local SQLite fallback
    database_url: str = Field(
        default="sqlite+aiosqlite:///./quizit.db",
        validation_alias="DATABASE_URL",
    )

    # Primary database: Supabase PostgreSQL
    supabase_database_url: str | None = Field(
        default=None,
        validation_alias="SUPABASE_DATABASE_URL",
    )

    redis_url: str | None = Field(
        default=None,
        validation_alias="REDIS_URL",
    )

    jwt_secret: str | None = Field(
        default=None,
        validation_alias="JWT_SECRET",
    )

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    cors_origins: str = Field(
        default="*",
        validation_alias="CORS_ORIGINS",
    )

    auto_create_tables: bool = Field(
        default=True,
        validation_alias="AUTO_CREATE_TABLES",
    )

    cookie_secure: bool = Field(
        default=False,
        validation_alias="COOKIE_SECURE",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def async_database_url(self) -> str:
        """
        Use Supabase PostgreSQL when SUPABASE_DATABASE_URL is configured.
        Convert PostgreSQL URLs to SQLAlchemy's asyncpg driver format.
        """
        database_url = self.supabase_database_url or self.database_url

        if database_url.startswith("postgresql://"):
            return database_url.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )

        if database_url.startswith("postgres://"):
            return database_url.replace(
                "postgres://",
                "postgresql+asyncpg://",
                1,
            )

        return database_url

    @property
    def jwt_signing_secret(self) -> str:
        return (
            self.jwt_secret
            or os.getenv("SESSION_SECRET")
            or "change-me-in-production"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
