"""Configuration settings for the A2A Agent Registry."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "A2A Agent Registry"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8000

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/a2a_registry"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # OpenSearch
    opensearch_url: str = "http://localhost:9200"
    opensearch_index: str = "a2a_agents"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Auth (JWKS / OAuth2)
    jwks_url: str = "https://auth.example.com/.well-known/jwks.json"
    token_issuer: Optional[str] = None
    token_audience: Optional[str] = None
    role_claim: str = "roles"
    tenant_claim: str = "tenant"
    client_id_claim: str = "client_id"

    # Registry
    registry_base_url: str = "http://localhost:8000"
    search_timeout_seconds: int = 30

    # DB bootstrap
    auto_create_tables: bool = False
    auto_create_index: bool = False

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
