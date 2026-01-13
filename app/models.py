from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, Relationship, SQLModel, String, Text


class MediaType(str, Enum):
    """Enum for different types of media assets."""
    SLIDE = "slide"
    IMAGE = "image"
    YOUTUBE = "youtube"
    BLOG_LINK = "blog_link"
    HTML = "html"


class UserRole(str, Enum):
    """Enum for user roles in the system."""
    ADMIN = "admin"  # Super admin - full access
    SUB_ADMIN = "sub_admin"  # Can approve tags, manage content
    USER = "user"  # Regular user - can create content and request tags


class PendingTagStatus(str, Enum):
    """Enum for pending tag approval status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(SQLModel, table=True):
    """
    User account for the platform.

    Integrated with Supabase Auth for authentication.
    Supports three roles: admin, sub_admin, user.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    supabase_id: str = Field(sa_column=Column(String(64), unique=True, index=True))
    email: str = Field(sa_column=Column(String(255), unique=True, index=True))
    full_name: Optional[str] = Field(default=None, sa_column=Column(String(200)))
    role: UserRole = Field(default=UserRole.USER, sa_column=Column(String(20)))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    posts: List["Post"] = Relationship(back_populates="author")
    pending_tags: List["PendingTag"] = Relationship(
        back_populates="requested_by_user",
        sa_relationship_kwargs={"foreign_keys": "[PendingTag.requested_by_id]"}
    )


class PostTag(SQLModel, table=True):
    """Junction table for many-to-many relationship between Posts and Tags."""
    post_id: int = Field(foreign_key="post.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)


class Tag(SQLModel, table=True):
    """
    Hierarchical tag system for organizing posts/modules.

    Tags can have parent-child relationships to create hierarchies like:
    - Reinforcement Learning
      ├── The RL Problem
      └── Markov Decision Processes
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(100), unique=True, index=True))
    slug: str = Field(sa_column=Column(String(100), unique=True, index=True))
    parent_id: Optional[int] = Field(default=None, foreign_key="tag.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Self-referential relationship for hierarchy
    parent: Optional["Tag"] = Relationship(
        sa_relationship_kwargs={"remote_side": "Tag.id"}
    )

    # Many-to-many with Post
    posts: List["Post"] = Relationship(back_populates="tags", link_model=PostTag)


class PendingTag(SQLModel, table=True):
    """
    Tag requests that require admin/sub-admin approval.

    Users can request new tags or subtags. Sub-admins or admins
    must approve before the tag is created in the Tag table.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(100), index=True))
    slug: str = Field(sa_column=Column(String(100), index=True))
    parent_id: Optional[int] = Field(default=None, foreign_key="tag.id")
    requested_by_id: int = Field(foreign_key="user.id")
    status: PendingTagStatus = Field(
        default=PendingTagStatus.PENDING,
        sa_column=Column(String(20))
    )
    reviewed_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    reviewed_at: Optional[datetime] = Field(default=None)
    rejection_reason: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    requested_by_user: "User" = Relationship(
        back_populates="pending_tags",
        sa_relationship_kwargs={"foreign_keys": "[PendingTag.requested_by_id]"}
    )
    parent: Optional["Tag"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[PendingTag.parent_id]"}
    )


class Post(SQLModel, table=True):
    """
    Main content entity representing a module or article.

    Posts contain a title, markdown description, and can have multiple
    media assets (images, slides, videos, links, etc).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column(String(200)))
    slug: str = Field(sa_column=Column(String(200), unique=True, index=True))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    author_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    author: Optional["User"] = Relationship(back_populates="posts")
    media_assets: List["MediaAsset"] = Relationship(
        back_populates="post",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    tags: List["Tag"] = Relationship(back_populates="posts", link_model=PostTag)


class MediaAsset(SQLModel, table=True):
    """
    Media resources attached to posts.

    Supports different types:
    - slide: Google Slides embed URL
    - image: Handwritten notes or diagrams
    - youtube: YouTube video links
    - blog_link: External blog/article references
    - html: Custom HTML content/visualizations
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id")
    type: MediaType = Field(sa_column=Column(String(20)))
    url: Optional[str] = Field(default=None, sa_column=Column(String(500)))
    content: Optional[str] = Field(default=None, sa_column=Column(Text))
    title: Optional[str] = Field(default=None, sa_column=Column(String(200)))
    order: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship
    post: Post = Relationship(back_populates="media_assets")


class TagActivity(SQLModel, table=True):
    """
    Track tag activity metrics over time for analytics.

    Stores daily aggregated stats like contribution counts,
    number of posts, unique contributors per tag.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", index=True)
    date: datetime = Field(index=True)
    post_count: int = Field(default=0)
    contributor_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship
    tag: "Tag" = Relationship()
