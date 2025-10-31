"""Configuration management for Shopify Status Agent."""

import os
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""
    
    # LLM Configuration
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.1, env="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(default=1000, env="OPENAI_MAX_TOKENS")
    
    # Shopify Configuration
    shopify_shop: str = Field(default="", env="SHOPIFY_SHOP")
    shopify_api_version: str = Field(default="2024-07", env="SHOPIFY_API_VERSION")
    shopify_access_token: Optional[str] = Field(default=None, env="SHOPIFY_ACCESS_TOKEN")
    
    # Application Configuration
    mock_mode: bool = Field(default=True, env="MOCK_MODE")
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    
    @property
    def shopify_base_url(self) -> str:
        """Get Shopify API base URL."""
        if not self.shopify_shop:
            return ""
        return f"https://{self.shopify_shop}.myshopify.com/admin/api/{self.shopify_api_version}"
    
    @property
    def shopify_headers(self) -> dict:
        """Get Shopify API headers."""
        if not self.shopify_access_token:
            return {}
        return {
            "X-Shopify-Access-Token": self.shopify_access_token,
            "Content-Type": "application/json",
        }
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
