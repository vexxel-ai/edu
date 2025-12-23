"""
Tests for user authentication and user-related endpoints.
"""

from typing import Callable

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.models import User


def test_request_magic_link_creates_auth_request(
        client: TestClient
):
    """Test that requesting a magic link returns success."""
    # Use url_path_for to generate the URL from route name
    url = app.url_path_for("request_magic_link")

    response = client.post(
        url,
        json={"email": "newuser@example.com"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Magic link sent! Check your email to sign in."
    assert response.json()["email"] == "newuser@example.com"


def test_verify_token_creates_new_user(
        session: Session,
        client: TestClient
):
    """Test that verifying a token creates a new user in the database."""
    # Use url_path_for to generate the URL
    url = app.url_path_for("verify_token")

    response = client.post(
        url,
        json={"access_token": "fake-test-token"}
    )

    # Debug: print response if it fails
    if response.status_code != status.HTTP_200_OK:
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Authentication successful"

    # Verify user was created in database
    user_email = response.json()["user"]["email"]
    assert user_email == "test@example.com"

    # Check database
    from sqlmodel import select
    statement = select(User).where(User.email == user_email)
    user = session.exec(statement).first()

    assert user is not None
    assert user.email == "test@example.com"
    assert user.supabase_id == "test-supabase-id-123"


def test_verify_token_updates_existing_user(
        session: Session,
        client: TestClient,
        create_user: Callable[..., User]
):
    """Test that verifying a token updates an existing user's last_login."""
    # Create a user first
    existing_user = create_user(
        session=session,
        email="test@example.com",
        supabase_id="test-supabase-id-123"
    )
    original_last_login = existing_user.last_login

    # Verify token (should update the same user)
    url = app.url_path_for("verify_token")
    response = client.post(
        url,
        json={"access_token": "fake-test-token"}
    )

    assert response.status_code == status.HTTP_200_OK

    # Refresh the user from database
    session.refresh(existing_user)

    # last_login should be updated
    assert existing_user.last_login != original_last_login
    assert existing_user.last_login is not None


def test_get_current_user_returns_user_info(
        session: Session,
        client: TestClient,
        create_user: Callable[..., User]
):
    """Test that /me endpoint returns current user information."""
    # Create a user
    user = create_user(
        session=session,
        email="test@example.com",
        supabase_id="test-supabase-id-123"
    )

    # Use url_path_for for the endpoint
    url = app.url_path_for("get_current_user")

    response = client.get(
        url,
        headers={"Authorization": "Bearer fake-test-token"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "test@example.com"
    assert response.json()["uuid"] == str(user.uuid)


def test_get_current_user_requires_auth(client: TestClient):
    """Test that /me endpoint requires authentication."""
    url = app.url_path_for("get_current_user")

    # No authorization header
    response = client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_logout_invalidates_session(client: TestClient):
    """Test that logout endpoint works correctly."""
    url = app.url_path_for("logout")

    response = client.post(
        url,
        headers={"Authorization": "Bearer fake-test-token"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Successfully signed out"
