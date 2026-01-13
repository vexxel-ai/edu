"""
Authentication routes for user signup, signin, and session management.

Integrates with Supabase Auth and local User database.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from supabase import Client

from app.auth.dependencies import get_current_user
from app.auth.supabase_client import get_supabase_client
from app.database import get_session
from app.models import User, UserRole

router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response Models

class SignUpRequest(BaseModel):
    """Request model for user registration."""

    email: EmailStr
    password: str
    full_name: Optional[str] = None


class SignInRequest(BaseModel):
    """Request model for user login."""

    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Response model for authentication operations."""

    access_token: str
    refresh_token: str
    user: dict


class UserResponse(BaseModel):
    """Response model for user information."""

    id: int
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: str


class RefreshRequest(BaseModel):
    """Request model for token refresh."""

    refresh_token: str


# Routes


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(
    request: SignUpRequest,
    session: Session = Depends(get_session),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Register a new user account.

    Creates user in both Supabase Auth and local database.
    Default role is 'user'.

    Args:
        request: Sign up request with email, password, and optional full name
        session: Database session
        supabase: Supabase client

    Returns:
        Auth response with tokens and user info

    Raises:
        HTTPException: If email already exists or sign up fails
    """
    # Check if user already exists in local database
    existing_user = session.exec(select(User).where(User.email == request.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up(
            {
                "email": request.email,
                "password": request.password,
            }
        )

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user in authentication system",
            )

        # Create user record in local database
        user = User(
            supabase_id=auth_response.user.id,
            email=request.email,
            full_name=request.full_name,
            role=UserRole.USER,  # Default role
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        return AuthResponse(
            access_token=auth_response.session.access_token if auth_response.session else "",
            refresh_token=auth_response.session.refresh_token if auth_response.session else "",
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active,
            },
        )

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}",
        )


@router.post("/signin", response_model=AuthResponse)
async def sign_in(
    request: SignInRequest,
    session: Session = Depends(get_session),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Sign in an existing user.

    Authenticates with Supabase and syncs with local database.

    Args:
        request: Sign in request with email and password
        session: Database session
        supabase: Supabase client

    Returns:
        Auth response with tokens and user info

    Raises:
        HTTPException: If credentials are invalid or user not found
    """
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password(
            {
                "email": request.email,
                "password": request.password,
            }
        )

        if not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Get user from local database
        user = session.exec(select(User).where(User.email == request.email)).first()

        # If user doesn't exist in local DB, create it (sync from Supabase)
        if not user:
            user = User(
                supabase_id=auth_response.user.id,
                email=request.email,
                role=UserRole.USER,
                is_active=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated",
            )

        return AuthResponse(
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sign in failed: {str(e)}",
        )


@router.post("/signout")
async def sign_out(supabase: Client = Depends(get_supabase_client)):
    """
    Sign out current user.

    Invalidates the current session in Supabase.

    Args:
        supabase: Supabase client

    Returns:
        Success message
    """
    try:
        # Supabase client is sync, not async
        supabase.auth.sign_out()
        return {"message": "Signed out successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sign out failed: {str(e)}",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.

    Args:
        user: Current authenticated user from dependency

    Returns:
        User information
    """
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: RefreshRequest,
    session: Session = Depends(get_session),
    supabase: Client = Depends(get_supabase_client),
):
    """
    Refresh access token using refresh token.

    Args:
        request: Refresh request with refresh token
        session: Database session
        supabase: Supabase client

    Returns:
        New auth tokens and user info

    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        # Refresh session with Supabase
        auth_response = supabase.auth.refresh_session(request.refresh_token)

        if not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Get user from local database
        user = session.exec(
            select(User).where(User.supabase_id == auth_response.user.id)
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return AuthResponse(
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}",
        )
