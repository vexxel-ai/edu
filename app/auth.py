"""
Authentication service using Supabase for passwordless magic link authentication.

This module provides integration with Supabase Auth to handle user authentication
via email-based magic links. It manages user creation, session verification, and
synchronization between Supabase Auth and the local User database.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select
from supabase import Client, create_client

from app.models import User


class SupabaseAuthService:
    """
    Service for handling Supabase authentication operations.

    This service provides methods to:
    - Send magic link emails to users
    - Verify authentication tokens
    - Manage user sessions
    - Sync Supabase users with local User database
    """

    def __init__(self, supabase_url: str, supabase_key: str):
        """
        Initialize the Supabase Auth service.

        Args:
            supabase_url: The Supabase project URL
            supabase_key: The Supabase anonymous/public API key
        """
        self.client: Client = create_client(supabase_url, supabase_key)

    async def send_magic_link(self, email: str, redirect_url: Optional[str] = None) -> dict:
        """
        Send a magic link authentication email to the user.

        Args:
            email: The user's email address
            redirect_url: Optional URL to redirect to after authentication

        Returns:
            dict: Response from Supabase containing the result

        Raises:
            HTTPException: If the magic link request fails
        """
        try:
            options = {}
            if redirect_url:
                options["redirect_to"] = redirect_url

            response = self.client.auth.sign_in_with_otp({
                "email": email,
                "options": options
            })
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to send magic link: {str(e)}"
            )

    async def verify_token(self, access_token: str) -> dict:
        """
        Verify a Supabase access token and return user information.

        Args:
            access_token: The JWT access token from Supabase

        Returns:
            dict: User information from Supabase

        Raises:
            HTTPException: If token verification fails
        """
        try:
            response = self.client.auth.get_user(access_token)
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid or expired token: {str(e)}"
            )

    async def get_or_create_user(
        self,
        db: Session,
        email: str,
        supabase_id: str
    ) -> User:
        """
        Get an existing user or create a new one based on Supabase authentication.

        This method synchronizes Supabase Auth users with the local database.
        If a user with the given supabase_id exists, it's returned and last_login
        is updated. Otherwise, a new user is created.

        Args:
            db: Database session
            email: User's email address from Supabase
            supabase_id: User's ID from Supabase Auth

        Returns:
            User: The existing or newly created user

        Raises:
            HTTPException: If user creation/retrieval fails
        """
        try:
            # Try to find user by supabase_id first
            statement = select(User).where(User.supabase_id == supabase_id)
            user = db.exec(statement).first()

            if user:
                # Update last login
                user.last_login = datetime.now(timezone.utc)
                db.add(user)
                db.commit()
                db.refresh(user)
                return user

            # Try to find by email (in case user exists but supabase_id wasn't set)
            statement = select(User).where(User.email == email)
            user = db.exec(statement).first()

            if user:
                # Link existing user to Supabase
                user.supabase_id = supabase_id
                user.last_login = datetime.now(timezone.utc)
                db.add(user)
                db.commit()
                db.refresh(user)
                return user

            # Create new user
            user = User(
                email=email,
                supabase_id=supabase_id,
                last_login=datetime.now(timezone.utc)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create or retrieve user: {str(e)}"
            )

    async def sign_out(self, access_token: str) -> None:
        """
        Sign out a user by invalidating their Supabase session.

        Args:
            access_token: The user's current access token

        Raises:
            HTTPException: If sign out fails
        """
        try:
            self.client.auth.sign_out(access_token)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to sign out: {str(e)}"
            )


# Global auth service instance (to be initialized with config)
_auth_service: Optional[SupabaseAuthService] = None


def init_auth_service(supabase_url: str, supabase_key: str) -> None:
    """
    Initialize the global Supabase auth service.

    This should be called once during application startup with the
    Supabase configuration from environment variables.

    Args:
        supabase_url: The Supabase project URL
        supabase_key: The Supabase anonymous/public API key
    """
    global _auth_service
    _auth_service = SupabaseAuthService(supabase_url, supabase_key)


def get_auth_service() -> SupabaseAuthService:
    """
    Get the global Supabase auth service instance.

    Returns:
        SupabaseAuthService: The initialized auth service

    Raises:
        RuntimeError: If auth service hasn't been initialized
    """
    if _auth_service is None:
        raise RuntimeError(
            "Auth service not initialized. Call init_auth_service() during startup."
        )
    return _auth_service