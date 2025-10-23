"""Конфигурация приложения."""

from functools import lru_cache
from typing import Optional

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="CodeMetrics", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")

    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")

    # T1 Сфера.Код API
    sfera_api_url: str = Field(..., alias="SFERA_API_URL")
    sfera_api_username: str = Field(..., alias="SFERA_API_USERNAME")
    sfera_api_password: str = Field(..., alias="SFERA_API_PASSWORD")
    sfera_api_timeout: int = Field(default=30, alias="SFERA_API_TIMEOUT")

    # Database (optional for basic API functionality)
    database_url: str = Field(
        default="postgresql+asyncpg://codemetrics:password@localhost:5432/codemetrics",
        alias="DATABASE_URL"
    )
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    # Redis (optional)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL"
    )
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL")

    # Celery (optional)
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1",
        alias="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2",
        alias="CELERY_RESULT_BACKEND"
    )

    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        alias="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")

    # Data Collection
    collection_batch_size: int = Field(default=100, alias="COLLECTION_BATCH_SIZE")
    collection_interval_minutes: int = Field(
        default=60, alias="COLLECTION_INTERVAL_MINUTES"
    )
    max_workers: int = Field(default=4, alias="MAX_WORKERS")

    # Metrics
    metrics_retention_days: int = Field(default=90, alias="METRICS_RETENTION_DAYS")
    anomaly_threshold: float = Field(default=2.0, alias="ANOMALY_THRESHOLD")

    @property
    def is_production(self) -> bool:
        """Проверка на production окружение."""
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Получение настроек приложения (с кешированием)."""
    return Settings()
