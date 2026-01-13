from typing import Generator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine


# Database file path
database_file_path = Path(__file__).resolve().parent.parent / "database.db"
DATABASE_URL = f"sqlite:///{database_file_path}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query debugging
    connect_args={"check_same_thread": False}  # Needed for SQLite
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
