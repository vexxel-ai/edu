"""
Application configuration using environment variables.

This module loads configuration from environment variables for:
- Supabase authentication settings
- Database connection
- Application settings
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be configured via environment variables or a .env file.
    Supabase settings are required for authentication to work.
    """

    # Supabase Configuration
    supabase_url: str
    supabase_anon_key: str

    # Application Settings
    app_name: str = "Educational Platform"
    debug: bool = False

    # Frontend URL for magic link redirects
    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.

    This function caches the settings instance to avoid repeated
    environment variable reads.

    Returns:
        Settings: The application settings

    Raises:
        ValidationError: If required environment variables are missing
    """
    return Settings()
