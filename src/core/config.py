"""Configuration management using Pydantic BaseSettings."""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application configuration settings."""

    # Application
    app_name: str = "URL List Management API"
    debug: bool = True
    environment: Literal["development", "production", "testing"] = "development"

    # Database
    database_url: str = "sqlite:///./url_lists.db"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    reload: bool = True

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "text"] = "json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
