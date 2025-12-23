"""
Authentication router for handling magic link authentication endpoints.

This module provides FastAPI routes for:
- Requesting magic link emails
- Verifying authentication tokens
- User sign out
- Getting current user information
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlmodel import Session

from app.auth import get_auth_service, SupabaseAuthService
from app.dependency import get_session
from app.models import User


router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response Models
class MagicLinkRequest(BaseModel):
    """Request model for magic link authentication."""
    email: EmailStr
    redirect_url: str | None = None


class MagicLinkResponse(BaseModel):
    """Response model after requesting a magic link."""
    message: str
    email: str


class TokenVerifyRequest(BaseModel):
    """Request model for token verification."""
    access_token: str


class UserResponse(BaseModel):
    """Response model for user information."""
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    email: str
    created_at: str
    last_login: str | None


class AuthResponse(BaseModel):
    """Response model after successful authentication."""
    user: UserResponse
    message: str


@router.post("/magic-link", response_model=MagicLinkResponse, name="request_magic_link")
async def request_magic_link(
    request: MagicLinkRequest,
    auth_service: Annotated[SupabaseAuthService, Depends(get_auth_service)]
):
    """
    Send a magic link authentication email to the user.

    This endpoint initiates passwordless authentication by sending an email
    with a magic link to the provided email address. The user clicks the link
    to authenticate.

    Args:
        request: Contains the user's email and optional redirect URL
        auth_service: Injected Supabase auth service

    Returns:
        MagicLinkResponse: Confirmation that the email was sent

    Raises:
        HTTPException: If the email sending fails
    """
    await auth_service.send_magic_link(
        email=request.email,
        redirect_url=request.redirect_url
    )

    return MagicLinkResponse(
        message="Magic link sent! Check your email to sign in.",
        email=request.email
    )


@router.post("/verify", response_model=AuthResponse, name="verify_token")
async def verify_token(
    request: TokenVerifyRequest,
    db: Annotated[Session, Depends(get_session)],
    auth_service: Annotated[SupabaseAuthService, Depends(get_auth_service)]
):
    """
    Verify an authentication token and create/update user session.

    After clicking the magic link, the frontend receives a token from Supabase.
    This endpoint verifies that token, retrieves user information from Supabase,
    and creates or updates the user in the local database.

    Args:
        request: Contains the access token to verify
        db: Database session
        auth_service: Injected Supabase auth service

    Returns:
        AuthResponse: User information and success message

    Raises:
        HTTPException: If token verification fails
    """
    # Verify token with Supabase
    supabase_user = await auth_service.verify_token(request.access_token)

    # Extract user info from Supabase response
    user_data = supabase_user.user
    if not user_data or not user_data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user data from Supabase"
        )

    # Get or create user in local database
    user = await auth_service.get_or_create_user(
        db=db,
        email=user_data.email,
        supabase_id=user_data.id
    )

    return AuthResponse(
        user=UserResponse(
            uuid=str(user.uuid),
            email=user.email,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        ),
        message="Authentication successful"
    )


@router.post("/logout", name="logout")
async def logout(
    authorization: Annotated[str | None, Header()] = None,
    auth_service: Annotated[SupabaseAuthService, Depends(get_auth_service)] = None
):
    """
    Sign out the current user by invalidating their session.

    Args:
        authorization: Authorization header with Bearer token
        auth_service: Injected Supabase auth service

    Returns:
        dict: Success message

    Raises:
        HTTPException: If no authorization header or logout fails
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    access_token = authorization.replace("Bearer ", "")
    await auth_service.sign_out(access_token)

    return {"message": "Successfully signed out"}


@router.get("/me", response_model=UserResponse, name="get_current_user")
async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: Annotated[Session, Depends(get_session)] = None,
    auth_service: Annotated[SupabaseAuthService, Depends(get_auth_service)] = None
):
    """
    Get the currently authenticated user's information.

    This endpoint verifies the provided token and returns the user's
    information from the local database.

    Args:
        authorization: Authorization header with Bearer token
        db: Database session
        auth_service: Injected Supabase auth service

    Returns:
        UserResponse: Current user's information

    Raises:
        HTTPException: If not authenticated or user not found
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    access_token = authorization.replace("Bearer ", "")

    # Verify token with Supabase
    supabase_user = await auth_service.verify_token(access_token)
    user_data = supabase_user.user

    if not user_data or not user_data.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Get user from database
    from sqlmodel import select
    statement = select(User).where(User.supabase_id == user_data.id)
    user = db.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        uuid=str(user.uuid),
        email=user.email,
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )