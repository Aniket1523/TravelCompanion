from __future__ import annotations

from supabase import Client

from exceptions import AuthenticationError, ConflictError, ValidationError
from logging_config import logger


def signup(client: Client, email: str, password: str) -> dict:
    """Register a new user via Supabase Auth.

    Uses the anon client — no Authorization header required.

    Returns a dict always containing access_token, refresh_token, user_id, and
    email_confirmation_required. When Supabase has email confirmation enabled,
    sign_up succeeds but result.session is None; we return empty token strings
    AND email_confirmation_required=True so the frontend can branch cleanly
    instead of persisting empty tokens and getting 401s on the next request.
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
    email_confirmation_required = session is None
    if email_confirmation_required:
        logger.info(
            "User signed up, email confirmation required: %s", result.user.id
        )
    else:
        logger.info("User signed up with active session: %s", result.user.id)
    return {
        "access_token": session.access_token if session else "",
        "refresh_token": session.refresh_token if session else "",
        "user_id": str(result.user.id),
        "email_confirmation_required": email_confirmation_required,
    }


def login(client: Client, email: str, password: str) -> dict:
    """Authenticate a user via email/password."""
    try:
        result = client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception as e:
        error_msg = str(e).lower()
        # Supabase returns "Email not confirmed" when the user hasn't clicked
        # the confirmation link yet. Give the UI a specific, actionable message
        # instead of a generic "invalid credentials" (which misleads the user).
        if "email not confirmed" in error_msg or "confirm your email" in error_msg:
            raise AuthenticationError(
                "Please confirm your email before signing in. "
                "Check your inbox for the confirmation link."
            )
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


def resend_confirmation(client: Client, email: str) -> dict:
    """Resend the Supabase signup confirmation email.

    Swallows Supabase errors intentionally — we must not reveal whether a given
    email is registered (that would enable account enumeration). The response
    is always the same generic success message.
    """
    try:
        client.auth.resend({"type": "signup", "email": email})
    except Exception as e:
        # Log server-side only; never surface to caller.
        logger.info("Resend confirmation attempt for %s: %s", email, e)
    return {
        "message": (
            "If an account exists for this email, a confirmation link "
            "has been sent."
        )
    }
