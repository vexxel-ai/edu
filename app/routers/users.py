"""
User management routes.

Admin-only endpoints for managing users, roles, and permissions.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session, func, select

from app.auth.dependencies import require_admin
from app.auth.utils import get_user_stats
from app.database import get_session
from app.models import PendingSection, PendingSubsection, Post, User, UserRole

router = APIRouter(prefix="/users", tags=["users"])


# Request/Response Models


class UserListResponse(BaseModel):
    """Response model for user list item."""

    id: int
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: str
    post_count: int
    pending_request_count: int


class UserDetailResponse(BaseModel):
    """Response model for detailed user information."""

    id: int
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: str
    supabase_id: str
    stats: dict


class UserRoleUpdateRequest(BaseModel):
    """Request model for updating user role."""

    role: str


class UserStatusUpdateRequest(BaseModel):
    """Request model for activating/deactivating user."""

    is_active: bool


class UserListPaginatedResponse(BaseModel):
    """Response model for paginated user list."""

    users: list[UserListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Routes


@router.get("", response_model=UserListPaginatedResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by email or name"),
    user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """
    List all users with pagination and filtering.

    Only accessible to admins.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        role: Optional role filter
        is_active: Optional active status filter
        search: Optional search query for email/name
        user: Current authenticated admin user
        session: Database session

    Returns:
        Paginated list of users with statistics
    """
    # Build base query
    query = select(User)

    # Apply filters
    if role:
        try:
            role_enum = UserRole(role)
            query = query.where(User.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}",
            )

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (User.email.ilike(search_pattern)) | (User.full_name.ilike(search_pattern))
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(User.created_at.desc())

    # Execute query
    users = session.exec(query).all()

    # Build response with stats
    user_responses = []
    for u in users:
        # Count posts
        post_count = session.exec(
            select(func.count()).where(Post.author_id == u.id)
        ).one()

        # Count pending sections
        pending_section_count = session.exec(
            select(func.count()).where(
                PendingSection.requested_by_id == u.id,
                PendingSection.status == "pending",
            )
        ).one()

        # Count pending subsections
        pending_subsection_count = session.exec(
            select(func.count()).where(
                PendingSubsection.requested_by_id == u.id,
                PendingSubsection.status == "pending",
            )
        ).one()

        pending_request_count = pending_section_count + pending_subsection_count

        user_responses.append(
            UserListResponse(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                role=u.role.value,
                is_active=u.is_active,
                created_at=u.created_at.isoformat(),
                post_count=post_count,
                pending_request_count=pending_request_count,
            )
        )

    total_pages = (total + page_size - 1) // page_size

    return UserListPaginatedResponse(
        users=user_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user_details(
    user_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """
    Get detailed information about a specific user.

    Only accessible to admins.

    Args:
        user_id: ID of the user to retrieve
        current_user: Current authenticated admin user
        session: Database session

    Returns:
        Detailed user information with statistics

    Raises:
        HTTPException: If user not found
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Get user statistics
    stats = get_user_stats(user)

    return UserDetailResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        supabase_id=user.supabase_id,
        stats=stats,
    )


@router.patch("/{user_id}/role")
async def update_user_role(
    user_id: int,
    request: UserRoleUpdateRequest,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """
    Update a user's role.

    Only accessible to admins.
    Admins cannot change their own role.

    Args:
        user_id: ID of the user to update
        request: New role information
        current_user: Current authenticated admin user
        session: Database session

    Returns:
        Updated user information

    Raises:
        HTTPException: If user not found or trying to change own role
    """
    # Prevent admins from changing their own role
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role",
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Validate and set new role
    try:
        new_role = UserRole(request.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {request.role}. Must be one of: admin, sub_admin, user",
        )

    old_role = user.role
    user.role = new_role
    session.add(user)
    session.commit()
    session.refresh(user)

    return {
        "message": "User role updated successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "old_role": old_role.value,
            "new_role": user.role.value,
        },
    }


@router.patch("/{user_id}/status")
async def update_user_status(
    user_id: int,
    request: UserStatusUpdateRequest,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """
    Activate or deactivate a user account.

    Only accessible to admins.
    Admins cannot deactivate their own account.

    Args:
        user_id: ID of the user to update
        request: New active status
        current_user: Current authenticated admin user
        session: Database session

    Returns:
        Updated user information

    Raises:
        HTTPException: If user not found or trying to deactivate own account
    """
    # Prevent admins from deactivating their own account
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own account status",
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.is_active = request.is_active
    session.add(user)
    session.commit()
    session.refresh(user)

    status_text = "activated" if request.is_active else "deactivated"

    return {
        "message": f"User account {status_text} successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
        },
    }


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """
    Delete a user account (soft delete by deactivating).

    Only accessible to admins.
    Admins cannot delete their own account.

    This performs a soft delete by setting is_active to False.
    The user record is not actually removed from the database.

    Args:
        user_id: ID of the user to delete
        current_user: Current authenticated admin user
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If user not found or trying to delete own account
    """
    # Prevent admins from deleting their own account
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Soft delete by deactivating
    user.is_active = False
    session.add(user)
    session.commit()

    return {
        "message": "User account deleted successfully",
        "user_id": user_id,
    }


@router.get("/stats/summary")
async def get_user_stats_summary(
    user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    """
    Get summary statistics about all users.

    Only accessible to admins.

    Args:
        user: Current authenticated admin user
        session: Database session

    Returns:
        User statistics summary
    """
    # Count users by role
    admin_count = session.exec(
        select(func.count()).where(User.role == UserRole.ADMIN)
    ).one()
    sub_admin_count = session.exec(
        select(func.count()).where(User.role == UserRole.SUB_ADMIN)
    ).one()
    user_count = session.exec(
        select(func.count()).where(User.role == UserRole.USER)
    ).one()

    # Count active/inactive users
    active_count = session.exec(
        select(func.count()).where(User.is_active == True)
    ).one()
    inactive_count = session.exec(
        select(func.count()).where(User.is_active == False)
    ).one()

    # Total users
    total = admin_count + sub_admin_count + user_count

    return {
        "total_users": total,
        "by_role": {
            "admin": admin_count,
            "sub_admin": sub_admin_count,
            "user": user_count,
        },
        "by_status": {
            "active": active_count,
            "inactive": inactive_count,
        },
    }
