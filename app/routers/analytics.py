"""
Analytics and metrics routes.

Provides tag activity tracking and contribution metrics (GitHub-like analytics).
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlmodel import Session, func, select

from app.auth.dependencies import get_current_user_optional
from app.database import get_session
from app.models import Post, PostTag, Tag, User

router = APIRouter(prefix="/analytics", tags=["analytics"])


# Response Models


class TagActivityDataPoint(BaseModel):
    """Data point for tag activity over time."""

    date: str
    post_count: int
    contributor_count: int


class TagActivityResponse(BaseModel):
    """Response model for tag activity analytics."""

    tag_id: int
    tag_name: str
    data_points: list[TagActivityDataPoint]
    total_posts: int
    total_contributors: int


class TopTagResponse(BaseModel):
    """Response model for top/most active tags."""

    tag_id: int
    tag_name: str
    slug: str
    post_count: int
    contributor_count: int
    parent_id: Optional[int]
    parent_name: Optional[str]


class ContributorResponse(BaseModel):
    """Response model for top contributors."""

    user_id: int
    email: str
    full_name: Optional[str]
    post_count: int
    tags_contributed: int


class TagStatsResponse(BaseModel):
    """Response model for overall tag statistics."""

    total_tags: int
    total_posts: int
    total_contributors: int
    most_active_tag: Optional[TopTagResponse]


# Routes


@router.get("/tags/{tag_id}/activity", response_model=TagActivityResponse)
async def get_tag_activity(
    tag_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    user: Optional[User] = Depends(get_current_user_optional),
    session: Session = Depends(get_session),
):
    """
    Get activity data for a specific tag over time.

    Shows posts created per day and unique contributors.

    Args:
        tag_id: ID of the tag to analyze
        days: Number of days to include in analysis
        user: Optional current user
        session: Database session

    Returns:
        Tag activity data with daily breakdown
    """
    # Verify tag exists
    tag = session.get(Tag, tag_id)
    if not tag:
        return TagActivityResponse(
            tag_id=tag_id,
            tag_name="Unknown",
            data_points=[],
            total_posts=0,
            total_contributors=0,
        )

    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    # Get all posts for this tag within date range
    posts_query = (
        select(Post)
        .join(PostTag, Post.id == PostTag.post_id)
        .where(
            PostTag.tag_id == tag_id,
            Post.created_at >= start_date,
            Post.created_at <= end_date,
        )
    )
    posts = session.exec(posts_query).all()

    # Group posts by date
    daily_data = {}
    all_contributors = set()

    for post in posts:
        date_key = post.created_at.date().isoformat()
        if date_key not in daily_data:
            daily_data[date_key] = {
                "post_count": 0,
                "contributors": set(),
            }
        daily_data[date_key]["post_count"] += 1
        if post.author_id:
            daily_data[date_key]["contributors"].add(post.author_id)
            all_contributors.add(post.author_id)

    # Build data points
    data_points = []
    current_date = start_date.date()
    while current_date <= end_date.date():
        date_key = current_date.isoformat()
        data = daily_data.get(date_key, {"post_count": 0, "contributors": set()})
        data_points.append(
            TagActivityDataPoint(
                date=date_key,
                post_count=data["post_count"],
                contributor_count=len(data["contributors"]),
            )
        )
        current_date += timedelta(days=1)

    # Get total stats
    total_posts_query = (
        select(func.count())
        .select_from(PostTag)
        .where(PostTag.tag_id == tag_id)
    )
    total_posts = session.exec(total_posts_query).one()

    return TagActivityResponse(
        tag_id=tag_id,
        tag_name=tag.name,
        data_points=data_points,
        total_posts=total_posts,
        total_contributors=len(all_contributors),
    )


@router.get("/tags/top", response_model=list[TopTagResponse])
async def get_top_tags(
    limit: int = Query(10, ge=1, le=50, description="Number of tags to return"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Filter by recent days"),
    user: Optional[User] = Depends(get_current_user_optional),
    session: Session = Depends(get_session),
):
    """
    Get most active tags by post count.

    Args:
        limit: Maximum number of tags to return
        days: Optional filter for recent activity
        user: Optional current user
        session: Database session

    Returns:
        List of most active tags with statistics
    """
    # Build base query
    query = (
        select(
            Tag.id,
            Tag.name,
            Tag.slug,
            Tag.parent_id,
            func.count(PostTag.post_id).label("post_count"),
        )
        .join(PostTag, Tag.id == PostTag.tag_id, isouter=True)
        .group_by(Tag.id, Tag.name, Tag.slug, Tag.parent_id)
    )

    # Add date filter if specified
    if days:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        query = (
            query.join(Post, PostTag.post_id == Post.id)
            .where(Post.created_at >= cutoff_date)
        )

    # Order by post count and limit
    query = query.order_by(func.count(PostTag.post_id).desc()).limit(limit)

    # Execute query
    results = session.exec(query).all()

    # Build response
    top_tags = []
    for tag_id, tag_name, slug, parent_id, post_count in results:
        # Get parent name if exists
        parent_name = None
        if parent_id:
            parent = session.get(Tag, parent_id)
            parent_name = parent.name if parent else None

        # Count unique contributors for this tag
        contributor_query = (
            select(func.count(func.distinct(Post.author_id)))
            .select_from(Post)
            .join(PostTag, Post.id == PostTag.post_id)
            .where(PostTag.tag_id == tag_id, Post.author_id.isnot(None))
        )
        contributor_count = session.exec(contributor_query).one()

        top_tags.append(
            TopTagResponse(
                tag_id=tag_id,
                tag_name=tag_name,
                slug=slug,
                post_count=post_count or 0,
                contributor_count=contributor_count,
                parent_id=parent_id,
                parent_name=parent_name,
            )
        )

    return top_tags


@router.get("/contributors/top", response_model=list[ContributorResponse])
async def get_top_contributors(
    limit: int = Query(10, ge=1, le=50, description="Number of contributors to return"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Filter by recent days"),
    tag_id: Optional[int] = Query(None, description="Filter by specific tag"),
    user: Optional[User] = Depends(get_current_user_optional),
    session: Session = Depends(get_session),
):
    """
    Get top contributors by post count.

    Args:
        limit: Maximum number of contributors to return
        days: Optional filter for recent activity
        tag_id: Optional filter for specific tag
        user: Optional current user
        session: Database session

    Returns:
        List of top contributors with statistics
    """
    # Build base query
    query = (
        select(
            User.id,
            User.email,
            User.full_name,
            func.count(Post.id).label("post_count"),
        )
        .join(Post, User.id == Post.author_id, isouter=True)
        .where(User.is_active == True)
        .group_by(User.id, User.email, User.full_name)
    )

    # Add date filter if specified
    if days:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        query = query.where(Post.created_at >= cutoff_date)

    # Add tag filter if specified
    if tag_id:
        query = query.join(PostTag, Post.id == PostTag.post_id).where(
            PostTag.tag_id == tag_id
        )

    # Order by post count and limit
    query = query.order_by(func.count(Post.id).desc()).limit(limit)

    # Execute query
    results = session.exec(query).all()

    # Build response
    contributors = []
    for user_id, email, full_name, post_count in results:
        # Count unique tags this user has contributed to
        tags_query = (
            select(func.count(func.distinct(PostTag.tag_id)))
            .select_from(Post)
            .join(PostTag, Post.id == PostTag.post_id)
            .where(Post.author_id == user_id)
        )
        tags_count = session.exec(tags_query).one()

        contributors.append(
            ContributorResponse(
                user_id=user_id,
                email=email,
                full_name=full_name,
                post_count=post_count or 0,
                tags_contributed=tags_count,
            )
        )

    return contributors


@router.get("/tags/stats", response_model=TagStatsResponse)
async def get_tag_stats(
    user: Optional[User] = Depends(get_current_user_optional),
    session: Session = Depends(get_session),
):
    """
    Get overall tag statistics.

    Args:
        user: Optional current user
        session: Database session

    Returns:
        Overall tag statistics
    """
    # Count total tags
    total_tags = session.exec(select(func.count()).select_from(Tag)).one()

    # Count total posts
    total_posts = session.exec(select(func.count()).select_from(Post)).one()

    # Count unique contributors (users who have created at least one post)
    total_contributors = session.exec(
        select(func.count(func.distinct(Post.author_id)))
        .select_from(Post)
        .where(Post.author_id.isnot(None))
    ).one()

    # Get most active tag
    most_active_query = (
        select(
            Tag.id,
            Tag.name,
            Tag.slug,
            Tag.parent_id,
            func.count(PostTag.post_id).label("post_count"),
        )
        .join(PostTag, Tag.id == PostTag.tag_id, isouter=True)
        .group_by(Tag.id, Tag.name, Tag.slug, Tag.parent_id)
        .order_by(func.count(PostTag.post_id).desc())
        .limit(1)
    )
    result = session.exec(most_active_query).first()

    most_active_tag = None
    if result:
        tag_id, tag_name, slug, parent_id, post_count = result
        # Get parent name if exists
        parent_name = None
        if parent_id:
            parent = session.get(Tag, parent_id)
            parent_name = parent.name if parent else None

        # Count contributors
        contributor_query = (
            select(func.count(func.distinct(Post.author_id)))
            .select_from(Post)
            .join(PostTag, Post.id == PostTag.post_id)
            .where(PostTag.tag_id == tag_id, Post.author_id.isnot(None))
        )
        contributor_count = session.exec(contributor_query).one()

        most_active_tag = TopTagResponse(
            tag_id=tag_id,
            tag_name=tag_name,
            slug=slug,
            post_count=post_count or 0,
            contributor_count=contributor_count,
            parent_id=parent_id,
            parent_name=parent_name,
        )

    return TagStatsResponse(
        total_tags=total_tags,
        total_posts=total_posts,
        total_contributors=total_contributors,
        most_active_tag=most_active_tag,
    )
