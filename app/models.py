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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
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


class AdminSession(SQLModel, table=True):
    """
    Simple session tracking for admin authentication.

    Stores session tokens to maintain admin login state.
    No complex user management - just a single admin password.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(sa_column=Column(String(64), unique=True, index=True))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
