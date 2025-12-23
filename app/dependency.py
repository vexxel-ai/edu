"""
Dependency injection functions for FastAPI.

This module provides dependency functions for:
- Database sessions
- Template rendering
- Authentication and user verification
"""

import os
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db import engine
from app.models import User

_templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


def _get_templates():
    """Get the Jinja2 templates instance."""
    return _templates


Templates = Annotated[Jinja2Templates, Depends(_get_templates)]


def get_session():
    """
    Provide a database session for dependency injection.

    Yields:
        Session: A SQLModel database session
    """
    with Session(engine) as session:
        yield session


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: Annotated[Session, Depends(get_session)] = None
) -> User:
    """
    Get the currently authenticated user from the request.

    This dependency extracts the Bearer token from the Authorization header,
    verifies it with Supabase, and returns the corresponding User from the database.

    Args:
        authorization: Authorization header containing Bearer token
        db: Database session

    Returns:
        User: The authenticated user

    Raises:
        HTTPException: If authentication fails or user not found

    Example:
        @app.get("/protected")
        async def protected_route(
            user: Annotated[User, Depends(get_current_user)]
        ):
            return {"user_id": user.uuid}
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = authorization.replace("Bearer ", "")

    # Import here to avoid circular dependency
    from app.auth import get_auth_service

    try:
        auth_service = get_auth_service()
        supabase_user = await auth_service.verify_token(access_token)
        user_data = supabase_user.user

        if not user_data or not user_data.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Get user from database
        statement = select(User).where(User.supabase_id == user_data.id)
        user = db.exec(statement).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


# Type alias for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]