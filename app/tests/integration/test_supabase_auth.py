"""
Integration tests for Supabase authentication.

These tests require a real Supabase project and valid credentials.
They are skipped by default and must be run explicitly.

Setup:
1. Create a test Supabase project at https://app.supabase.com
2. Add credentials to .env:
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
3. Run: pytest -m integration

IMPORTANT: Use a separate TEST project, not your production Supabase!
"""

import os

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.auth import SupabaseAuthService, init_auth_service
from app.dependency import get_session
from app.main import app
from app.models import User


# Skip all tests in this file if Supabase credentials are not configured
pytestmark = pytest.mark.skipif(
    not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_ANON_KEY"),
    reason="Supabase credentials not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY"
)


@pytest.fixture(name="test_session")
def test_session_fixture():
    """
    Create test database session for integration tests.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="integration_client")
def integration_client_fixture(test_session: Session):
    """
    Create test client with real Supabase but test database.
    """
    def get_session_override():
        return test_session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="real_auth_service")
def real_auth_service_fixture():
    """
    Create a real SupabaseAuthService instance for testing.
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    return SupabaseAuthService(
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )


class TestSupabaseMagicLink:
    """Test magic link functionality with real Supabase API."""

    @pytest.mark.integration
    async def test_send_magic_link_success(self, real_auth_service):
        """
        Test sending magic link with real Supabase.

        NOTE: This will send a real email! Use a test email you control.
        You can configure a test email in the environment variable TEST_EMAIL.
        """
        test_email = os.getenv("TEST_EMAIL", "test@example.com")

        # This should not raise an exception
        result = await real_auth_service.send_magic_link(
            email=test_email,
            redirect_url="http://localhost:3000/auth/callback"
        )

        # Supabase returns different response structures, just verify no exception
        assert result is not None

    @pytest.mark.integration
    async def test_send_magic_link_invalid_email(self, real_auth_service):
        """Test that invalid email formats are handled."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            await real_auth_service.send_magic_link(
                email="not-an-email",
                redirect_url="http://localhost:3000"
            )

    @pytest.mark.integration
    def test_magic_link_endpoint(self, integration_client):
        """Test the /auth/magic-link endpoint with real Supabase."""
        test_email = os.getenv("TEST_EMAIL", "test@example.com")

        response = integration_client.post(
            "/auth/magic-link",
            json={"email": test_email}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Magic link sent! Check your email to sign in."
        assert response.json()["email"] == test_email


class TestSupabaseTokenVerification:
    """Test token verification with real Supabase."""

    @pytest.mark.integration
    async def test_verify_invalid_token(self, real_auth_service):
        """Test that invalid tokens are rejected."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await real_auth_service.verify_token("invalid-token-12345")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    async def test_verify_empty_token(self, real_auth_service):
        """Test that empty tokens are rejected."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            await real_auth_service.verify_token("")


class TestSupabaseUserCreation:
    """Test user creation flow with real Supabase."""

    @pytest.mark.integration
    async def test_get_or_create_user_creates_new(
        self,
        real_auth_service,
        test_session
    ):
        """Test creating a new user in the database."""
        user = await real_auth_service.get_or_create_user(
            db=test_session,
            email="newuser@example.com",
            supabase_id="test-supabase-id-unique"
        )

        assert user is not None
        assert user.email == "newuser@example.com"
        assert user.supabase_id == "test-supabase-id-unique"
        assert user.last_login is not None

    @pytest.mark.integration
    async def test_get_or_create_user_updates_existing(
        self,
        real_auth_service,
        test_session
    ):
        """Test updating an existing user's last_login."""
        # Create user first
        user1 = await real_auth_service.get_or_create_user(
            db=test_session,
            email="existing@example.com",
            supabase_id="test-supabase-id-existing"
        )
        first_login = user1.last_login

        # Get same user again
        user2 = await real_auth_service.get_or_create_user(
            db=test_session,
            email="existing@example.com",
            supabase_id="test-supabase-id-existing"
        )

        assert user1.uuid == user2.uuid
        assert user2.last_login >= first_login


class TestSupabaseSignOut:
    """Test sign out functionality."""

    @pytest.mark.integration
    async def test_sign_out_invalid_token(self, real_auth_service):
        """Test sign out with invalid token."""
        from fastapi import HTTPException

        # Supabase might handle invalid tokens differently
        # This test documents the behavior
        with pytest.raises(HTTPException):
            await real_auth_service.sign_out("invalid-token")


class TestEndToEndAuthFlow:
    """
    End-to-end authentication tests.

    NOTE: These tests require manual intervention (clicking magic link in email)
    and are marked as manual. They serve as documentation for manual testing.
    """

    @pytest.mark.integration
    @pytest.mark.manual
    def test_complete_auth_flow_documentation(self):
        """
        Document the complete authentication flow for manual testing.

        This is not an automated test but serves as documentation.

        Manual Testing Steps:
        1. Start the server: uvicorn app.main:app --reload
        2. Request magic link:
           curl -X POST http://localhost:8000/auth/magic-link \
             -H "Content-Type: application/json" \
             -d '{"email": "your-email@example.com"}'
        3. Check your email and click the magic link
        4. Extract the access_token from the redirect URL
        5. Verify the token:
           curl -X POST http://localhost:8000/auth/verify \
             -H "Content-Type: application/json" \
             -d '{"access_token": "YOUR_TOKEN_HERE"}'
        6. Check your user info:
           curl -X GET http://localhost:8000/auth/me \
             -H "Authorization: Bearer YOUR_TOKEN_HERE"
        7. Sign out:
           curl -X POST http://localhost:8000/auth/logout \
             -H "Authorization: Bearer YOUR_TOKEN_HERE"
        """
        pytest.skip("This is a manual test - see docstring for instructions")


# Helper function for manual testing
def print_integration_test_instructions():
    """
    Print instructions for running integration tests.

    Run this with: python -c "from app.tests.integration.test_supabase_auth import print_integration_test_instructions; print_integration_test_instructions()"
    """
    return """
    ╔════════════════════════════════════════════════════════════════╗
    ║       Supabase Integration Testing Instructions               ║
    ╚════════════════════════════════════════════════════════════════╝

    1. Setup (one-time):
       • Create a TEST Supabase project at https://app.supabase.com
       • DO NOT use your production project!
       • Copy your project URL and anon key
       • Add to .env file:
         SUPABASE_URL=https://your-test-project.supabase.co
         SUPABASE_ANON_KEY=your-test-anon-key
         TEST_EMAIL=your-test-email@example.com

    2. Run integration tests:
       pytest -m integration

    3. Run specific test:
       pytest -m integration -k test_send_magic_link

    4. Skip integration tests (default):
       pytest -m "not integration"

    5. Manual E2E test:
       pytest -m manual  # See test docstrings for instructions

    ╔════════════════════════════════════════════════════════════════╗
    ║  IMPORTANT: These tests will send real emails and create      ║
    ║  real data in Supabase. Always use a TEST project!            ║
    ╚════════════════════════════════════════════════════════════════╝
    """


if __name__ == "__main__":
    print(print_integration_test_instructions())