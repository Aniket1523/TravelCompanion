from __future__ import annotations

from supabase import Client

from exceptions import AuthenticationError, ConflictError
from logging_config import logger


def signup(client: Client, email: str, password: str) -> dict:
    """Register a new user via Supabase Auth."""
    try:
        result = client.auth.sign_up({"email": email, "password": password})
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            raise ConflictError("A user with this email already exists")
        logger.error("Signup failed for %s: %s", email, error_msg)
        raise AuthenticationError("Signup failed")

    if not result.user:
        raise AuthenticationError("Signup failed")

    session = result.session
    logger.info("User signed up: %s", result.user.id)
    return {
        "access_token": session.access_token if session else "",
        "refresh_token": session.refresh_token if session else "",
        "user_id": str(result.user.id),
    }


def login(client: Client, email: str, password: str) -> dict:
    """Authenticate a user via email/password."""
    try:
        result = client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception:
        raise AuthenticationError("Invalid email or password")

    if not result.user or not result.session:
        raise AuthenticationError("Invalid email or password")

    logger.info("User logged in: %s", result.user.id)
    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
        "user_id": str(result.user.id),
    }


def refresh_token(client: Client, refresh_token_value: str) -> dict:
    """Refresh an access token."""
    try:
        result = client.auth.refresh_session(refresh_token_value)
    except Exception:
        raise AuthenticationError("Invalid or expired refresh token")

    if not result.user or not result.session:
        raise AuthenticationError("Token refresh failed")

    logger.info("Token refreshed for user: %s", result.user.id)
    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
        "user_id": str(result.user.id),
    }


def logout(client: Client, access_token: str) -> dict:
    """Sign out the current user."""
    try:
        scoped = client
        scoped.auth.sign_out()
    except Exception:
        pass  # Best-effort logout
    logger.info("User logged out")
    return {"message": "Logged out successfully"}
