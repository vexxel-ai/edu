"""
Tag management routes (simplified).

Tags are optional, flat (no hierarchy), and don't require approval.
Anyone can create tags for additional filtering.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.database import get_session
from app.models import Tag, User

router = APIRouter(prefix="/tags", tags=["tags"])


# ==================== Request/Response Models ====================


class TagCreate(BaseModel):
    """Request model for creating a tag."""
    name: str
    slug: str


class TagResponse(BaseModel):
    """Response model for tags."""
    id: int
    name: str
    slug: str
    created_at: str


# ==================== Public Routes ====================


@router.get("/", response_model=list[TagResponse])
async def list_tags(session: Session = Depends(get_session)):
    """
    Get all tags.

    Public endpoint - no authentication required.
    """
    tags = session.exec(select(Tag).order_by(Tag.name)).all()
    return [
        TagResponse(
            id=t.id,
            name=t.name,
            slug=t.slug,
            created_at=t.created_at.isoformat(),
        )
        for t in tags
    ]


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: int, session: Session = Depends(get_session)):
    """
    Get a specific tag by ID.

    Public endpoint - no authentication required.
    """
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return TagResponse(
        id=tag.id,
        name=tag.name,
        slug=tag.slug,
        created_at=tag.created_at.isoformat(),
    )


# ==================== User Routes (Create) ====================


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    request: TagCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Create a new tag.

    Requires authentication. No approval needed - tags are created immediately.
    """
    # Check if tag already exists
    existing = session.exec(
        select(Tag).where((Tag.name == request.name) | (Tag.slug == request.slug))
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name or slug already exists",
        )

    # Create tag directly (no approval needed)
    new_tag = Tag(
        name=request.name,
        slug=request.slug,
    )
    session.add(new_tag)
    session.commit()
    session.refresh(new_tag)

    return TagResponse(
        id=new_tag.id,
        name=new_tag.name,
        slug=new_tag.slug,
        created_at=new_tag.created_at.isoformat(),
    )
