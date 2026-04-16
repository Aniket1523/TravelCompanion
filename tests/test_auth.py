"""Tests for auth endpoints."""

from unittest.mock import patch


@patch("routers.auth.get_anon_client")
@patch("routers.auth.auth_service")
def test_signup(mock_service, mock_client, client):
    mock_service.signup.return_value = {
        "access_token": "tok-123",
        "refresh_token": "ref-123",
        "user_id": "new-user-id",
    }

    response = client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "securepassword"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["access_token"] == "tok-123"
    assert data["user_id"] == "new-user-id"


@patch("routers.auth.get_anon_client")
@patch("routers.auth.auth_service")
def test_login(mock_service, mock_client, client):
    mock_service.login.return_value = {
        "access_token": "tok-456",
        "refresh_token": "ref-456",
        "user_id": "existing-user-id",
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
