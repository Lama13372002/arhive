"""Application configuration."""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings."""
    
    # ====== APP ======
    app_name: str = "Sunog API"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # ====== SECURITY ======
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # ====== DATABASE ======
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "sunog"
    postgres_user: str = "sunog"
    postgres_password: str
    
    @property
    def database_url(self) -> str:
        """Get database URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def sync_database_url(self) -> str:
        """Get synchronous database URL for Alembic."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    # ====== REDIS ======
    redis_url: str = "redis://localhost:6379/0"
    
    # ====== TELEGRAM ======
    telegram_bot_token: str
    telegram_bot_webhook_secret: str
    telegram_webhook_url: Optional[str] = None
    
    # ====== AI ======
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    
    # ====== SUNO ======
    use_suno: bool = False
    suno_api_key: Optional[str] = None
    suno_api_base: str = "https://api.sunoapi.org"
    
    # ====== S3 STORAGE ======
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    s3_bucket_name: str = "sunog-assets"
    s3_region: str = "us-east-1"
    
    # ====== PAYMENTS ======
    payment_provider: str = "stripe"
    stripe_publishable_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # ====== URLS ======
    base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    public_base_url: str = "http://localhost:8000"
    
    # ====== BUSINESS RULES ======
    max_free_regenerations: int = 3
    asset_retention_days: int = 180
    rate_limit_per_minute: int = 30
    
    # ====== OBSERVABILITY ======
    sentry_dsn: Optional[str] = None
    prometheus_enabled: bool = True
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

