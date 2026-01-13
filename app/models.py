"""
Data models for edu.vexxel.ai with Section/Subsection structure.

Structure:
- Section: Top-level categories (e.g., "Reinforcement Learning")
- Subsection: Second-level categories (e.g., "Q-Learning")
- Post: Content modules (must have section + subsection)
- Tag: Optional flat tags for filtering (no approval needed)
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, UniqueConstraint
from sqlmodel import Column, Field, Relationship, SQLModel, String, Text


class MediaType(str, Enum):
    """Enum for different types of media assets."""

    SLIDE = "slide"
    IMAGE = "image"
    YOUTUBE = "youtube"
    BLOG_LINK = "blog_link"
    CODE_SNIPPET = "code_snippet"
    EXERCISE = "exercise"


class UserRole(str, Enum):
    """Enum for user roles in the system."""

    ADMIN = "admin"  # Super admin - full access
    SUB_ADMIN = "sub_admin"  # Can approve sections/subsections, manage content
    USER = "user"  # Regular user - can create content and request sections/subsections


class PendingStatus(str, Enum):
    """Enum for pending approval status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# ==================== Core Structure: Sections & Subsections ====================


class Section(SQLModel, table=True):
    """
    Top-level content category.

    Examples: "Reinforcement Learning", "Deep Learning", "Algorithms"

    Every post MUST belong to exactly one section.
    Sections require admin approval before creation.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(100), unique=True, index=True))
    slug: str = Field(sa_column=Column(String(100), unique=True, index=True))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    subsections: list["Subsection"] = Relationship(back_populates="section")
    posts: list["Post"] = Relationship(back_populates="section")


class Subsection(SQLModel, table=True):
    """
    Second-level content category within a Section.

    Examples: "Q-Learning" (under Reinforcement Learning), "CNNs" (under Deep Learning)

    Every post MUST belong to exactly one subsection.
    Subsections require admin approval before creation.

    Note: Slug is unique within a section (not globally).
    """

    __table_args__ = (UniqueConstraint("section_id", "slug", name="uq_subsection_section_slug"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(100), index=True))
    slug: str = Field(sa_column=Column(String(100), index=True))
    section_id: int = Field(foreign_key="section.id")
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    section: Section = Relationship(back_populates="subsections")
    posts: list["Post"] = Relationship(back_populates="subsection")


class PendingSection(SQLModel, table=True):
    """
    Section creation requests requiring admin approval.

    Users can request new sections. Admins or sub-admins must approve.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(100), index=True))
    slug: str = Field(sa_column=Column(String(100), index=True))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    requested_by_id: int = Field(foreign_key="user.id")
    status: PendingStatus = Field(default=PendingStatus.PENDING, sa_column=Column(String(20)))
    reviewed_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    reviewed_at: Optional[datetime] = Field(default=None)
    rejection_reason: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    requested_by_user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[PendingSection.requested_by_id]"}
    )


class PendingSubsection(SQLModel, table=True):
    """
    Subsection creation requests requiring admin approval.

    Users can request new subsections within existing sections.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(100), index=True))
    slug: str = Field(sa_column=Column(String(100), index=True))
    section_id: int = Field(foreign_key="section.id")
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    requested_by_id: int = Field(foreign_key="user.id")
    status: PendingStatus = Field(default=PendingStatus.PENDING, sa_column=Column(String(20)))
    reviewed_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    reviewed_at: Optional[datetime] = Field(default=None)
    rejection_reason: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    requested_by_user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[PendingSubsection.requested_by_id]"}
    )
    section: Section = Relationship()


# ==================== Optional Tags for Filtering ====================


class PostTag(SQLModel, table=True):
    """Junction table for optional many-to-many relationship between Posts and Tags."""

    post_id: int = Field(foreign_key="post.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)


class Tag(SQLModel, table=True):
    """
    Optional tags for additional filtering and categorization.

    Unlike the old hierarchical tag system, these are flat tags.
    Tags are optional and don't require approval.

    Examples: "neural-networks", "optimization", "python", "theory"
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(100), unique=True, index=True))
    slug: str = Field(sa_column=Column(String(100), unique=True, index=True))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Many-to-many with Post
    posts: list["Post"] = Relationship(back_populates="tags", link_model=PostTag)


# ==================== Users ====================


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
    posts: list["Post"] = Relationship(
        back_populates="author",
        sa_relationship_kwargs={"foreign_keys": "[Post.author_id]"}
    )


# ==================== Posts & Media ====================


class Post(SQLModel, table=True):
    """
    Main content entity representing a module or article.

    REQUIRED:
    - section_id: Every post must belong to a section
    - subsection_id: Every post must belong to a subsection

    OPTIONAL:
    - tags: Posts can have zero or more tags for filtering

    APPROVAL WORKFLOW:
    - is_approved: False by default, requires admin/sub-admin approval
    - approved_by_id: Admin who approved the post
    - approved_at: Timestamp of approval
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column(String(200)))
    slug: str = Field(sa_column=Column(String(200), unique=True, index=True))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))

    # REQUIRED: Section and Subsection
    section_id: int = Field(foreign_key="section.id")
    subsection_id: int = Field(foreign_key="subsection.id")

    # Optional author
    author_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Approval workflow
    is_approved: bool = Field(default=False, sa_column=Column(Boolean, index=True))
    approved_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    approved_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    section: Section = Relationship(back_populates="posts")
    subsection: Subsection = Relationship(back_populates="posts")
    author: Optional[User] = Relationship(
        back_populates="posts",
        sa_relationship_kwargs={"foreign_keys": "[Post.author_id]"}
    )
    media_assets: list["MediaAsset"] = Relationship(
        back_populates="post", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    tags: list[Tag] = Relationship(back_populates="posts", link_model=PostTag)


class MediaAsset(SQLModel, table=True):
    """
    Media resources attached to posts.

    Supports different types:
    - slide: Google Slides embed URL
    - image: Handwritten notes or diagrams
    - youtube: YouTube video links
    - blog_link: External blog/article references
    - code_snippet: Code examples (content field stores code, url stores language)
    - exercise: Practice problems (content field stores markdown with question/solution)
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


# ==================== Analytics ====================
# Note: Activity tracking should be done at the Post level if needed
# (e.g., view counts, likes, etc. as fields on the Post model)
