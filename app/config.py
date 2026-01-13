"""
Application configuration and environment validation.
"""

import logging
import os
from typing import Optional

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Uses pydantic-settings for validation and type checking.
    """

    # Database
    database_url: Optional[str] = None

    # Supabase (updated to new API key structure)
    supabase_url: str
    supabase_api_key: str  # New API key (replaces legacy anon_key)
    supabase_jwt_secret: str

    # Admin
    super_admin_email: str
    super_admin_password: str

    # Environment
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False


def validate_environment() -> Settings:
    """
    Validate required environment variables on startup.

    Raises:
        ValueError: If required environment variables are missing or invalid

    Returns:
        Settings object with validated configuration
    """
    try:
        settings = Settings()

        # Log configuration (without secrets)
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Database URL configured: {bool(settings.database_url)}")
        logger.info(f"Supabase URL: {settings.supabase_url}")

        # Validate Supabase configuration
        if not settings.supabase_url.startswith("https://"):
            logger.warning("Supabase URL should start with https://")

        if len(settings.supabase_api_key) < 20:
            logger.warning("Supabase API key seems too short")

        if len(settings.supabase_jwt_secret) < 20:
            logger.warning("Supabase JWT secret seems too short")

        # Validate admin credentials
        if "@" not in settings.super_admin_email:
            raise ValueError("SUPER_ADMIN_EMAIL must be a valid email address")

        if len(settings.super_admin_password) < 8:
            logger.warning("SUPER_ADMIN_PASSWORD is weak (less than 8 characters)")

        logger.info("✓ Environment validation successful")
        return settings

    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        logger.error("Please check your .env file and ensure all required variables are set")
        logger.error("Required variables: SUPABASE_URL, SUPABASE_API_KEY, SUPABASE_JWT_SECRET, SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD")
        raise


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings singleton.

    Returns:
        Settings object
    """
    global settings
    if settings is None:
        settings = validate_environment()
    return settings
