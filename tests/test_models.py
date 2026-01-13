"""
Tests for database models.
"""

from datetime import datetime, timezone

import pytest
from sqlmodel import Session, select

from app.models import (
    MediaAsset,
    MediaType,
    PendingTag,
    PendingTagStatus,
    Post,
    PostTag,
    Tag,
    User,
    UserRole,
)


def test_create_user(session: Session):
    """Test creating a user."""
    user = User(
        supabase_id="test-123",
        email="test@example.com",
        full_name="Test User",
        role=UserRole.USER,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.role == UserRole.USER
    assert user.is_active is True


def test_create_tag(session: Session):
    """Test creating a tag."""
    tag = Tag(name="Test Tag", slug="test-tag")
    session.add(tag)
    session.commit()
    session.refresh(tag)

    assert tag.id is not None
    assert tag.name == "Test Tag"
    assert tag.slug == "test-tag"
    assert tag.parent_id is None


def test_hierarchical_tags(session: Session):
    """Test parent-child tag relationships."""
    parent = Tag(name="Parent", slug="parent")
    session.add(parent)
    session.commit()
    session.refresh(parent)

    child = Tag(name="Child", slug="child", parent_id=parent.id)
    session.add(child)
    session.commit()
    session.refresh(child)

    assert child.parent_id == parent.id


def test_create_post(session: Session):
    """Test creating a post."""
    post = Post(
        title="Test Post",
        slug="test-post",
        description="Test description",
    )
    session.add(post)
    session.commit()
    session.refresh(post)

    assert post.id is not None
    assert post.title == "Test Post"
    assert post.slug == "test-post"


def test_post_with_media_assets(session: Session):
    """Test post with media assets relationship."""
    post = Post(title="Test Post", slug="test-post")
    session.add(post)
    session.commit()
    session.refresh(post)

    # Add media assets
    image = MediaAsset(
        post_id=post.id,
        type=MediaType.IMAGE,
        url="/test.jpg",
        order=1,
    )
    slide = MediaAsset(
        post_id=post.id,
        type=MediaType.SLIDE,
        url="/slides",
        order=2,
    )
    session.add_all([image, slide])
    session.commit()

    # Verify relationship
    session.refresh(post)
    assert len(post.media_assets) == 2
    assert post.media_assets[0].type == MediaType.IMAGE
    assert post.media_assets[1].type == MediaType.SLIDE


def test_post_tag_relationship(session: Session):
    """Test many-to-many post-tag relationship."""
    # Create post and tags
    post = Post(title="Test Post", slug="test-post")
    tag1 = Tag(name="Tag 1", slug="tag-1")
    tag2 = Tag(name="Tag 2", slug="tag-2")

    session.add_all([post, tag1, tag2])
    session.commit()
    session.refresh(post)
    session.refresh(tag1)
    session.refresh(tag2)

    # Create relationships
    session.add(PostTag(post_id=post.id, tag_id=tag1.id))
    session.add(PostTag(post_id=post.id, tag_id=tag2.id))
    session.commit()

    # Verify
    post_tags = session.exec(select(PostTag).where(PostTag.post_id == post.id)).all()
    assert len(post_tags) == 2


def test_pending_tag(session: Session):
    """Test pending tag creation."""
    user = User(supabase_id="test-123", email="test@example.com", role=UserRole.USER)
    session.add(user)
    session.commit()
    session.refresh(user)

    pending = PendingTag(
        name="New Tag",
        slug="new-tag",
        requested_by_id=user.id,
        status=PendingTagStatus.PENDING,
    )
    session.add(pending)
    session.commit()
    session.refresh(pending)

    assert pending.id is not None
    assert pending.status == PendingTagStatus.PENDING
    assert pending.requested_by_id == user.id


def test_user_roles():
    """Test user role enum values."""
    assert UserRole.ADMIN == "admin"
    assert UserRole.SUB_ADMIN == "sub_admin"
    assert UserRole.USER == "user"


def test_media_types():
    """Test media type enum values."""
    assert MediaType.IMAGE == "image"
    assert MediaType.SLIDE == "slide"
    assert MediaType.YOUTUBE == "youtube"
    assert MediaType.BLOG_LINK == "blog_link"
    assert MediaType.HTML == "html"


def test_pending_tag_status():
    """Test pending tag status enum values."""
    assert PendingTagStatus.PENDING == "pending"
    assert PendingTagStatus.APPROVED == "approved"
    assert PendingTagStatus.REJECTED == "rejected"
