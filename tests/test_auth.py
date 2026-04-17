"""Tests for auth endpoints."""

from unittest.mock import patch


@patch("routers.auth.get_anon_client")
@patch("routers.auth.auth_service")
def test_signup(mock_service, mock_client, client):
    mock_service.signup.return_value = {
        "access_token": "tok-123",
        "refresh_token": "ref-123",
        "user_id": "new-user-id",
        "email_confirmation_required": False,
    }

    response = client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "securepassword"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["access_token"] == "tok-123"
    assert data["user_id"] == "new-user-id"
    assert data["email_confirmation_required"] is False


@patch("routers.auth.get_anon_client")
@patch("routers.auth.auth_service")
def test_signup_email_confirmation_required(mock_service, mock_client, client):
    """When Supabase has email confirmation enabled, signup returns empty
    tokens AND email_confirmation_required=True so the frontend knows not to
    persist tokens."""
    mock_service.signup.return_value = {
        "access_token": "",
        "refresh_token": "",
        "user_id": "unconfirmed-user-id",
        "email_confirmation_required": True,
    }

    response = client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "securepassword"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["access_token"] == ""
    assert data["refresh_token"] == ""
    assert data["user_id"] == "unconfirmed-user-id"
    assert data["email_confirmation_required"] is True


@patch("routers.auth.get_anon_client")
@patch("routers.auth.auth_service")
def test_resend_confirmation(mock_service, mock_client, client):
    mock_service.resend_confirmation.return_value = {
        "message": (
            "If an account exists for this email, a confirmation link "
            "has been sent."
        )
    }

    response = client.post(
        "/auth/resend-confirmation",
        json={"email": "test@example.com"},
    )

    assert response.status_code == 200
    assert "confirmation link" in response.json()["message"]


@patch("routers.auth.get_anon_client")
@patch("routers.auth.auth_service")
def test_login(mock_service, mock_client, client):
    mock_service.login.return_value = {
        "access_token": "tok-456",
        "refresh_token": "ref-456",
        "user_id": "existing-user-id",
        "email_confirmation_required": False,
    }

    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "securepassword"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "tok-456"


@patch("routers.auth.get_anon_client")
@patch("routers.auth.auth_service")
def test_refresh(mock_service, mock_client, client):
    mock_service.refresh_token.return_value = {
        "access_token": "tok-789",
        "refresh_token": "ref-789",
        "user_id": "user-id",
        "email_confirmation_required": False,
    }

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": "ref-456"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "tok-789"


def test_signup_invalid_email(client):
    response = client.post(
        "/auth/signup",
        json={"email": "x", "password": "securepassword"},
    )
    assert response.status_code == 422


def test_signup_short_password(client):
    response = client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "short"},
    )
    assert response.status_code == 422
