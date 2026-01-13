import os
from typing import Generator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine


# Get database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    # Default to SQLite for local development
    database_file_path = Path(__file__).resolve().parent.parent / "database.db"
    DATABASE_URL = f"sqlite:///{database_file_path}"

# Determine if using SQLite
is_sqlite = DATABASE_URL.startswith("sqlite")

# Create engine with appropriate settings
if is_sqlite:
    # SQLite-specific configuration
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL query debugging
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connections before using
    )


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes to get database session.

    Usage:
        @app.get("/posts")
        def get_posts(session: Session = Depends(get_session)):
            posts = session.exec(select(Post)).all()
            return posts
    """
    with Session(engine) as session:
        yield session
