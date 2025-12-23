import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.auth import get_auth_service
from app.dependency import get_session
from app.main import app
from app.models import User


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """
    Set up test environment variables.

    This fixture automatically runs before all tests and sets dummy
    Supabase credentials so the app can initialize without errors.
    """
    os.environ["SUPABASE_URL"] = "http://test-supabase.local"
    os.environ["SUPABASE_ANON_KEY"] = "test-key-123"
    yield
    # Cleanup after all tests
    os.environ.pop("SUPABASE_URL", None)
    os.environ.pop("SUPABASE_ANON_KEY", None)


@pytest.fixture(name="session")
def session_fixture():
    """
    Create an in-memory SQLite database session for testing.

    This fixture creates a temporary database that exists only in memory,
    sets up all SQLModel tables, and provides a session for database operations.
    The database is automatically cleaned up after each test.

    Yields:
        Session: A SQLModel session connected to the in-memory test database.
    """

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool  # Ensure all connections use the same in-memory DB
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


async def mock_get_or_create_user(db: Session, email: str, supabase_id: str) -> User:
    """
    Mock implementation of get_or_create_user for testing.

    Works with test database session to create or update users during auth flow.
    """
    # Try to find existing user by supabase_id
    statement = select(User).where(User.supabase_id == supabase_id)
    user = db.exec(statement).first()

    if user:
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.add(user)
        db.flush()  # Use flush instead of commit to keep transaction open
        return user

    # Try to find by email
    statement = select(User).where(User.email == email)
    user = db.exec(statement).first()

    if user:
        # Link to Supabase
        user.supabase_id = supabase_id
        user.last_login = datetime.now(timezone.utc)
        db.add(user)
        db.flush()
        return user

    # Create new user
    user = User(
        email=email,
        supabase_id=supabase_id,
        last_login=datetime.now(timezone.utc)
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture(name="mock_auth_service")
def mock_auth_service_fixture():
    """
    Mock Supabase auth service for testing.

    This fixture creates a mock auth service that simulates Supabase
    authentication without requiring real Supabase credentials. It returns
    fake user data and can be used to test auth flows.

    Returns:
        Mock: A mocked SupabaseAuthService instance
    """
    mock_service = Mock()

    # Mock send_magic_link
    mock_service.send_magic_link = AsyncMock(return_value={"message": "Magic link sent"})

    # Mock verify_token - returns a fake user
    mock_user_data = Mock()
    mock_user_data.id = "test-supabase-id-123"
    mock_user_data.email = "test@example.com"

    mock_response = Mock()
    mock_response.user = mock_user_data

    mock_service.verify_token = AsyncMock(return_value=mock_response)

    # Mock sign_out
    mock_service.sign_out = AsyncMock(return_value=None)

    # Use the top-level mock_get_or_create_user function
    mock_service.get_or_create_user = mock_get_or_create_user

    return mock_service


@pytest.fixture(name="client")
def client_fixture(session: Session, mock_auth_service):
    """
    Create a FastAPI test client with a test database session.

    This fixture overrides the application's database dependency to use the
    test session fixture, allowing tests to interact with the API using
    the in-memory test database. Also mocks the Supabase auth service.

    Args:
        session: The test database session from the session_fixture.
        mock_auth_service: Mocked auth service

    Yields:
        TestClient: A FastAPI test client configured with the test database.
    """

    def get_session_override():
        return session

    def get_auth_service_override():
        return mock_auth_service

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_auth_service] = get_auth_service_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def create_user():
    """
    Factory fixture for creating test users.

    This fixture returns a function that creates User instances in the database.
    Email is required; a default test email is provided but can be overridden.

    Returns:
        A function that accepts a session and optional kwargs to create a User.

    Example:
        def test_something(session, create_user):
            user = create_user(session)  # Uses default test@example.com
            # or with custom email:
            user = create_user(session, email="custom@test.com")
    """

    def _create_user(session: Session, **kwargs):
        # Provide default email if not specified
        if "email" not in kwargs:
            kwargs["email"] = "test@example.com"

        user = User(**kwargs)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    return _create_user
