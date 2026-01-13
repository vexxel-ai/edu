"""
Authentication module for edu.vexxel.ai

Provides Supabase authentication integration with JWT validation.
"""

from app.auth.dependencies import get_current_user, require_admin, require_sub_admin
from app.auth.supabase_client import get_supabase_client, settings

__all__ = [
    "get_current_user",
    "require_admin",
    "require_sub_admin",
    "get_supabase_client",
    "settings",
]
