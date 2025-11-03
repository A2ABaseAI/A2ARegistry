import os
from typing import Optional

from pydantic import BaseModel


class Settings(BaseModel):
    env: str = os.getenv("ENV", "local")
    registry_url: str = os.getenv("REGISTRY_URL", "http://localhost:8000")
    registry_client_id: Optional[str] = os.getenv("REGISTRY_CLIENT_ID")
    registry_client_secret: Optional[str] = os.getenv("REGISTRY_CLIENT_SECRET")
    registry_api_key: Optional[str] = os.getenv("REGISTRY_API_KEY", "dev-admin-api-key")  # Default to dev API key
    load_agents_on_startup: bool = os.getenv("LOAD_AGENTS_ON_STARTUP", "true").lower() == "true"
    agents_refresh_interval: int = int(os.getenv("AGENTS_REFRESH_INTERVAL", "300"))  # 5 minutes default


settings = Settings()
