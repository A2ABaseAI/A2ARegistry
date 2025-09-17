"""Configuration settings for the A2A Agent Registry."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "A2A Agent Registry"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/a2a_registry"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Elasticsearch
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "a2a_agents"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # OAuth2
    oauth2_client_id: str = "a2a-registry"
    oauth2_client_secret: str = "your-oauth2-secret"
    oauth2_token_url: str = "http://localhost:8000/oauth/token"

    # Registry
    registry_base_url: str = "http://localhost:8000"
    max_agents_per_client: int = 1000
    search_timeout_seconds: int = 30

    # Federation
    enable_federation: bool = True
    max_peer_registries: int = 10
    peer_sync_interval_minutes: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
