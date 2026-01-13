"""
Supabase client initialization and settings.

Provides configuration and client instance for Supabase authentication.
"""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from supabase import Client, create_client


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase configuration (updated to use new API key structure)
    supabase_url: str
    supabase_api_key: str  # Replaces legacy anon_key
    supabase_jwt_secret: str  # Still needed for JWT validation

    # Super admin configuration
    super_admin_email: str = "admin@vexxel.ai"
    super_admin_password: str = "change-this-in-production"

    # Database
    database_url: str = "sqlite:///./database.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses LRU cache to avoid recreating settings on every call.
    """
    return Settings()


# Global settings instance
settings = get_settings()


def get_supabase_client() -> Client:
    """
    Get Supabase client instance.

    Returns:
        Supabase client configured with URL and API key.
    """
    return create_client(settings.supabase_url, settings.supabase_api_key)
