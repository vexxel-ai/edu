"""
Pytest configuration and fixtures for testing.
"""

import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """
    Create a test database session.

    Uses an in-memory SQLite database for fast, isolated tests.
    """
    # Use in-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with dependency overrides.

    Overrides the database session to use test database.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """Set environment variables for testing."""
    os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
    os.environ.setdefault("SUPABASE_API_KEY", "test-api-key")
    os.environ.setdefault("SUPABASE_JWT_SECRET", "test-jwt-secret")
    os.environ.setdefault("SUPER_ADMIN_EMAIL", "admin@test.com")
    os.environ.setdefault("SUPER_ADMIN_PASSWORD", "testpassword")
