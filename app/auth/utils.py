"""
Authentication utility functions.

Helper functions for user management, role checking, and password handling.
"""

import re
from typing import Optional

from app.models import User, UserRole


def is_admin(user: User) -> bool:
    """
    Check if user has admin role.

    Args:
        user: User object to check

    Returns:
        True if user is admin, False otherwise
    """
    return user.role == UserRole.ADMIN


def is_sub_admin_or_admin(user: User) -> bool:
    """
    Check if user has sub-admin or admin role.

    Args:
        user: User object to check

    Returns:
        True if user is sub-admin or admin, False otherwise
    """
    return user.role in [UserRole.ADMIN, UserRole.SUB_ADMIN]


def can_approve_tags(user: User) -> bool:
    """
    Check if user can approve tag requests.

    Args:
        user: User object to check

    Returns:
        True if user can approve tags (sub-admin or admin)
    """
    return is_sub_admin_or_admin(user)


def can_manage_users(user: User) -> bool:
    """
    Check if user can manage other users.

    Args:
        user: User object to check

    Returns:
        True if user is admin (only admins can manage users)
    """
    return is_admin(user)


def can_change_role(actor: User, target_role: UserRole) -> bool:
    """
    Check if user can assign a specific role to another user.

    Args:
        actor: User attempting to change role
        target_role: Role to be assigned

    Returns:
        True if actor can assign target_role, False otherwise

    Rules:
        - Only admins can assign roles
        - Admins can assign any role
    """
    return is_admin(actor)


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def get_role_display_name(role: UserRole) -> str:
    """
    Get human-readable display name for role.

    Args:
        role: UserRole enum value

    Returns:
        Display name for the role
    """
    role_names = {
        UserRole.ADMIN: "Administrator",
        UserRole.SUB_ADMIN: "Sub-Administrator",
        UserRole.USER: "User",
    }
    return role_names.get(role, "Unknown")


def get_user_stats(user: User) -> dict:
    """
    Get statistics for a user.

    Args:
        user: User object

    Returns:
        Dictionary with user statistics
    """
    return {
        "total_posts": len(user.posts) if user.posts else 0,
        "pending_tag_requests": (
            len([pt for pt in user.pending_tags if pt.status.value == "pending"])
            if user.pending_tags
            else 0
        ),
        "approved_tag_requests": (
            len([pt for pt in user.pending_tags if pt.status.value == "approved"])
            if user.pending_tags
            else 0
        ),
    }
