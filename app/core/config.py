"""
Centralized, type-validated settings loaded from environment variables.

Precedence: real environment variables > .env file > defaults below.
That means the exact same code runs locally (via .env), in CI, and in
staging/production (via secrets injected as real env vars) with zero
environment-specific branching in application code.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "local"  # local | staging | production
    debug: bool = True
    log_level: str = "INFO"

    app_name: str = "MedDocAI"
    api_v1_prefix: str = "/api/v1"
    secret_key: str
    access_token_expire_minutes: int = 60

    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str

    # Cache + rate limiting only — not a task queue. Temporal owns all
    # background/durable execution (see app/workflows/).
    redis_host: str
    redis_port: int = 6379

    object_storage_endpoint: str
    object_storage_bucket: str
    object_storage_access_key: str
    object_storage_secret_key: str

    temporal_host: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def is_local(self) -> bool:
        return self.environment == "local"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"


@lru_cache
def get_settings() -> Settings:
    # cached so the environment is only ever parsed once per process
    return Settings()
