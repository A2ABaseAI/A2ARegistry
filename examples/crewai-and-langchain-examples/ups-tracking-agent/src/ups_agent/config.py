"""Configuration management for UPS Tracking Agent."""

import os
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""
    
    # UPS API Configuration
    ups_client_id: str = Field(..., env="UPS_CLIENT_ID", description="UPS API client ID")
    ups_client_secret: str = Field(..., env="UPS_CLIENT_SECRET", description="UPS API client secret")
    ups_account_number: Optional[str] = Field(default=None, env="UPS_ACCOUNT_NUMBER", description="UPS account number")
    ups_api_base: str = Field(default="https://onlinetools.ups.com", env="UPS_API_BASE", description="UPS API base URL")
    ups_use_sandbox: bool = Field(default=False, env="UPS_USE_SANDBOX", description="Use UPS sandbox environment")
    
    # Application Configuration
    debug: bool = Field(default=False, env="DEBUG", description="Debug mode")
    log_level: str = Field(default="INFO", env="LOG_LEVEL", description="Logging level")
    
    # CrewAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY", description="OpenAI API key for CrewAI")
    crewai_model: str = Field(default="gpt-4o-mini", env="CREWAI_MODEL", description="CrewAI model")
    crewai_temperature: float = Field(default=0.1, env="CREWAI_TEMPERATURE", description="CrewAI temperature")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        """Initialize settings with UPS sandbox configuration."""
        super().__init__(**kwargs)
        
        # Auto-configure sandbox if requested
        if self.ups_use_sandbox:
            self.ups_api_base = "https://wwwcie.ups.com"
    
    def validate_ups_credentials(self) -> None:
        """Validate UPS credentials are present."""
        if not self.ups_client_id:
            raise ValueError("UPS_CLIENT_ID is required")
        if not self.ups_client_secret:
            raise ValueError("UPS_CLIENT_SECRET is required")
    
    def validate_openai_credentials(self) -> None:
        """Validate OpenAI credentials are present."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for CrewAI")


# Global settings instance
settings = Settings()
