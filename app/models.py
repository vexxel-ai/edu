from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel, Column, String, Text


class User(SQLModel, table=True):
    """
    User model for application users authenticated via Supabase.

    Users are authenticated using passwordless magic links through Supabase Auth.
    The email field is unique and serves as the user's identifier for authentication.
    The supabase_id links to the Supabase Auth user for session management.
    """
    uuid: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(sa_column=Column(String(255), unique=True, index=True))
    supabase_id: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), unique=True, nullable=True, index=True)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_login: Optional[datetime] = None

    # Relationships
    progress: List["Progress"] = Relationship(back_populates="user")


class Course(SQLModel, table=True):
    uuid: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(sa_column=Column(String(100)))
    description: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    lessons: List["Lesson"] = Relationship(back_populates="course")


class Lesson(SQLModel, table=True):
    uuid: UUID = Field(default_factory=uuid4, primary_key=True)
    course_id: UUID = Field(foreign_key="course.uuid")
    slug: str = Field(sa_column=Column(String(100), unique=True, index=True))
    title: str = Field(sa_column=Column(String(100)))
    content: Optional[str] = Field(default=None, sa_column=Column(Text))
    order: int
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    course: Course = Relationship(back_populates="lessons")
    progress: List["Progress"] = Relationship(back_populates="lesson")


class Progress(SQLModel, table=True):
    uuid: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.uuid")
    lesson_id: UUID = Field(foreign_key="lesson.uuid")
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None

    # Relationships
    user: User = Relationship(back_populates="progress")
    lesson: Lesson = Relationship(back_populates="progress")
