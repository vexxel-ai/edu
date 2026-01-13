"""
Authentication dependencies for FastAPI routes.

Provides dependencies for JWT validation, user extraction, and role-based access control.
"""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.auth.supabase_client import settings
from app.database import get_session
from app.models import User, UserRole

# HTTP Bearer token authentication
security = HTTPBearer(auto_error=False)


async def get_current_user_email(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """
    Extract and validate user email from JWT token.

    Args:
        credentials: HTTP Authorization header with Bearer token

    Returns:
        User email from JWT payload

    Raises:
        HTTPException: If token is missing or invalid
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Decode JWT token using Supabase JWT secret
        payload = jwt.decode(
            credentials.credentials,
            settings.supabase_jwt_secret,
            audience="authenticated",
            algorithms=["HS256"],
        )
        email = payload.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: email not found",
            )
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
        )


async def get_current_user(
    email: str = Depends(get_current_user_email),
    session: Session = Depends(get_session),
) -> User:
    """
    Get current user from database by email.

    Args:
        email: User email from JWT token
        session: Database session

    Returns:
        User object

    Raises:
        HTTPException: If user not found or inactive
    """
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in database",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return user


async def require_admin(
    user: User = Depends(get_current_user),
) -> User:
    """
    Require admin role for route access.

    Args:
        user: Current authenticated user

    Returns:
        User object if user is admin

    Raises:
        HTTPException: If user is not an admin
    """
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


async def require_sub_admin(
    user: User = Depends(get_current_user),
) -> User:
    """
    Require sub-admin or admin role for route access.

    Args:
        user: Current authenticated user

    Returns:
        User object if user is sub-admin or admin

    Raises:
        HTTPException: If user is neither sub-admin nor admin
    """
    if user.role not in [UserRole.ADMIN, UserRole.SUB_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sub-admin or admin access required",
        )
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    session: Session = Depends(get_session),
) -> User | None:
    """
    Get current user if authenticated, None otherwise.

    Useful for routes that optionally use authentication.

    Args:
        credentials: HTTP Authorization header with Bearer token
        session: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.supabase_jwt_secret,
            audience="authenticated",
            algorithms=["HS256"],
        )
        email = payload.get("email")
        if not email:
            return None

        user = session.exec(select(User).where(User.email == email)).first()
        if user and user.is_active:
            return user
        return None
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        return None
