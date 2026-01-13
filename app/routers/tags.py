"""
Tag management and approval system.

Handles tag creation requests from users and approval workflow for admins/sub-admins.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user, require_sub_admin
from app.database import get_session
from app.models import PendingTag, PendingTagStatus, Tag, User, UserRole

router = APIRouter(prefix="/tags", tags=["tags"])


# Request/Response Models


class TagRequestCreate(BaseModel):
    """Request model for creating a tag request."""

    name: str
    slug: str
    parent_id: Optional[int] = None


class TagRequestResponse(BaseModel):
    """Response model for tag requests."""

    id: int
    name: str
    slug: str
    parent_id: Optional[int]
    status: str
    requested_by_email: str
    created_at: str
    reviewed_at: Optional[str] = None
    reviewed_by_email: Optional[str] = None
    rejection_reason: Optional[str] = None


class TagApprovalRequest(BaseModel):
    """Request model for approving a tag."""

    approved: bool
    rejection_reason: Optional[str] = None


# User Routes (Tag Requests)


@router.post("/request", response_model=TagRequestResponse, status_code=status.HTTP_201_CREATED)
async def request_new_tag(
    request: TagRequestCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Request a new tag or subtag.

    Normal users must request tags, which require admin/sub-admin approval.
    Admins and sub-admins can create tags directly (see admin routes).

    Args:
        request: Tag request details
        user: Current authenticated user
        session: Database session

    Returns:
        Created pending tag request

    Raises:
        HTTPException: If tag name/slug already exists
    """
    # Check if tag already exists
    existing_tag = session.exec(
        select(Tag).where((Tag.name == request.name) | (Tag.slug == request.slug))
    ).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name or slug already exists",
        )

    # Check if there's already a pending request for this tag
    existing_request = session.exec(
        select(PendingTag).where(
            (PendingTag.name == request.name) | (PendingTag.slug == request.slug),
            PendingTag.status == PendingTagStatus.PENDING,
        )
    ).first()
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending request for this tag already exists",
        )

    # Validate parent tag exists if specified
    if request.parent_id:
        parent = session.get(Tag, request.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent tag not found",
            )

    # Create pending tag request
    pending_tag = PendingTag(
        name=request.name,
        slug=request.slug,
        parent_id=request.parent_id,
        requested_by_id=user.id,
        status=PendingTagStatus.PENDING,
    )
    session.add(pending_tag)
    session.commit()
    session.refresh(pending_tag)

    return TagRequestResponse(
        id=pending_tag.id,
        name=pending_tag.name,
        slug=pending_tag.slug,
        parent_id=pending_tag.parent_id,
        status=pending_tag.status.value,
        requested_by_email=user.email,
        created_at=pending_tag.created_at.isoformat(),
    )


@router.get("/my-requests", response_model=list[TagRequestResponse])
async def get_my_tag_requests(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get all tag requests submitted by the current user.

    Args:
        user: Current authenticated user
        session: Database session

    Returns:
        List of tag requests
    """
    pending_tags = session.exec(
        select(PendingTag)
        .where(PendingTag.requested_by_id == user.id)
        .order_by(PendingTag.created_at.desc())
    ).all()

    results = []
    for pt in pending_tags:
        reviewed_by_user = None
        if pt.reviewed_by_id:
            reviewed_by_user = session.get(User, pt.reviewed_by_id)

        results.append(
            TagRequestResponse(
                id=pt.id,
                name=pt.name,
                slug=pt.slug,
                parent_id=pt.parent_id,
                status=pt.status.value,
                requested_by_email=user.email,
                created_at=pt.created_at.isoformat(),
                reviewed_at=pt.reviewed_at.isoformat() if pt.reviewed_at else None,
                reviewed_by_email=reviewed_by_user.email if reviewed_by_user else None,
                rejection_reason=pt.rejection_reason,
            )
        )

    return results


# Admin/Sub-Admin Routes (Tag Approval)


@router.get("/pending", response_model=list[TagRequestResponse])
async def get_pending_tag_requests(
    user: User = Depends(require_sub_admin),
    session: Session = Depends(get_session),
):
    """
    Get all pending tag requests for review.

    Requires sub-admin or admin role.

    Args:
        user: Current authenticated admin/sub-admin user
        session: Database session

    Returns:
        List of pending tag requests
    """
    pending_tags = session.exec(
        select(PendingTag)
        .where(PendingTag.status == PendingTagStatus.PENDING)
        .order_by(PendingTag.created_at.asc())
    ).all()

    results = []
    for pt in pending_tags:
        requested_by = session.get(User, pt.requested_by_id)
        results.append(
            TagRequestResponse(
                id=pt.id,
                name=pt.name,
                slug=pt.slug,
                parent_id=pt.parent_id,
                status=pt.status.value,
                requested_by_email=requested_by.email if requested_by else "Unknown",
                created_at=pt.created_at.isoformat(),
            )
        )

    return results


@router.post("/approve/{pending_id}")
async def approve_tag_request(
    pending_id: int,
    approval: TagApprovalRequest,
    user: User = Depends(require_sub_admin),
    session: Session = Depends(get_session),
):
    """
    Approve or reject a pending tag request.

    Requires sub-admin or admin role.

    Args:
        pending_id: ID of the pending tag request
        approval: Approval decision and optional rejection reason
        user: Current authenticated admin/sub-admin user
        session: Database session

    Returns:
        Success message and tag info

    Raises:
        HTTPException: If pending tag not found or already reviewed
    """
    # Get pending tag
    pending_tag = session.get(PendingTag, pending_id)
    if not pending_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending tag request not found",
        )

    if pending_tag.status != PendingTagStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag request has already been {pending_tag.status.value}",
        )

    if approval.approved:
        # Check again if tag exists (in case it was created while pending)
        existing_tag = session.exec(
            select(Tag).where(
                (Tag.name == pending_tag.name) | (Tag.slug == pending_tag.slug)
            )
        ).first()
        if existing_tag:
            # Mark as rejected instead
            pending_tag.status = PendingTagStatus.REJECTED
            pending_tag.rejection_reason = "Tag was created by another user"
            pending_tag.reviewed_by_id = user.id
            pending_tag.reviewed_at = datetime.now(timezone.utc)
            session.add(pending_tag)
            session.commit()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag with this name or slug already exists",
            )

        # Create the actual tag
        new_tag = Tag(
            name=pending_tag.name,
            slug=pending_tag.slug,
            parent_id=pending_tag.parent_id,
        )
        session.add(new_tag)

        # Update pending tag status
        pending_tag.status = PendingTagStatus.APPROVED
        pending_tag.reviewed_by_id = user.id
        pending_tag.reviewed_at = datetime.now(timezone.utc)
        session.add(pending_tag)

        session.commit()
        session.refresh(new_tag)

        return {
            "message": "Tag request approved and tag created",
            "tag": {
                "id": new_tag.id,
                "name": new_tag.name,
                "slug": new_tag.slug,
                "parent_id": new_tag.parent_id,
            },
        }
    else:
        # Reject the tag request
        if not approval.rejection_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rejection reason is required when rejecting a tag",
            )

        pending_tag.status = PendingTagStatus.REJECTED
        pending_tag.rejection_reason = approval.rejection_reason
        pending_tag.reviewed_by_id = user.id
        pending_tag.reviewed_at = datetime.now(timezone.utc)
        session.add(pending_tag)
        session.commit()

        return {
            "message": "Tag request rejected",
            "rejection_reason": approval.rejection_reason,
        }


@router.post("/create-direct", response_model=dict)
async def create_tag_direct(
    request: TagRequestCreate,
    user: User = Depends(require_sub_admin),
    session: Session = Depends(get_session),
):
    """
    Create a tag directly without approval process.

    Only available to sub-admins and admins.

    Args:
        request: Tag creation request
        user: Current authenticated admin/sub-admin user
        session: Database session

    Returns:
        Created tag info

    Raises:
        HTTPException: If tag already exists
    """
    # Check if tag already exists
    existing_tag = session.exec(
        select(Tag).where((Tag.name == request.name) | (Tag.slug == request.slug))
    ).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name or slug already exists",
        )

    # Validate parent tag exists if specified
    if request.parent_id:
        parent = session.get(Tag, request.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent tag not found",
            )

    # Create tag directly
    new_tag = Tag(
        name=request.name,
        slug=request.slug,
        parent_id=request.parent_id,
    )
    session.add(new_tag)
    session.commit()
    session.refresh(new_tag)

    return {
        "message": "Tag created successfully",
        "tag": {
            "id": new_tag.id,
            "name": new_tag.name,
            "slug": new_tag.slug,
            "parent_id": new_tag.parent_id,
        },
    }
