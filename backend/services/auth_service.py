from __future__ import annotations

from supabase import Client

from exceptions import AuthenticationError, ConflictError, ValidationError
from logging_config import logger


def signup(client: Client, email: str, password: str) -> dict:
    """Register a new user via Supabase Auth.

    Uses the anon client — no Authorization header required.
    When email confirmation is enabled in Supabase the session will be None
    and empty token strings are returned; the user must confirm before login.
    """
    try:
        result = client.auth.sign_up({"email": email, "password": password})
    except Exception as e:
        error_msg = str(e).lower()
        # Supabase returns "User already registered" for duplicate emails.
        if "already registered" in error_msg:
            raise ConflictError("A user with this email already exists")
        # Supabase validation errors: weak password, invalid email format, etc.
        if "invalid" in error_msg or "weak" in error_msg or "password" in error_msg:
            raise ValidationError(str(e))
        logger.error("Signup error for %s: %s", email, e)
        raise  # let router convert to HTTPException(500) with CORS headers

    if not result.user:
        logger.error("Supabase sign_up returned no user for %s", email)
        raise AuthenticationError("Signup failed — please try again")

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
    except Exception as e:
        error_msg = str(e).lower()
        if (
            "invalid login" in error_msg
            or "invalid email" in error_msg
            or "wrong" in error_msg
            or "credentials" in error_msg
        ):
            raise AuthenticationError("Invalid email or password")
        if "invalid" in error_msg:
            raise ValidationError(str(e))
        logger.error("Login error: %s", e)
        raise  # let router convert to HTTPException(500) with CORS headers

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
