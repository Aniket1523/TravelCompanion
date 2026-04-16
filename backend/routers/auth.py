from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from auth import get_current_user
from db import get_anon_client, get_supabase_client
from exceptions import AuthenticationError, ConflictError, ValidationError
from logging_config import logger
from models.auth import AuthResponse, LoginRequest, RefreshRequest, SignupRequest
from rate_limit import limiter
from services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

_SERVER_ERROR = "An internal error occurred. Please try again later."


def _to_http(exc: Exception, context: str) -> HTTPException:
    """Convert an unexpected exception to HTTPException(500).

    HTTPException is handled by Starlette's ExceptionMiddleware, which sits
    INSIDE CORSMiddleware — so the 500 response will carry CORS headers and
    the browser won't see an additional CORS block on top of the real error.
    Raw exceptions that escape to ServerErrorMiddleware (outside CORS) produce
    500 responses with no CORS headers, causing a misleading double-failure.
    """
    logger.error("%s: %s", context, exc)
    return HTTPException(status_code=500, detail=_SERVER_ERROR)


@router.post("/signup", response_model=AuthResponse, status_code=201)
@limiter.limit("5/minute")
def signup(request: Request, body: SignupRequest):
    """Register a new user. Public endpoint — no Authorization header required.
    Rate-limited to 5/min per IP to deter abuse."""
    client = get_anon_client()
    try:
        return auth_service.signup(client=client, email=body.email, password=body.password)
    except (ConflictError, AuthenticationError, ValidationError):
        raise  # domain exceptions → proper 409 / 401 / 422 with CORS headers
    except Exception as exc:
        raise _to_http(exc, "Unexpected signup error") from exc


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
def login(request: Request, body: LoginRequest):
    """Authenticate with email and password. Public endpoint.
    Rate-limited to 10/min per IP."""
    client = get_anon_client()
    try:
        return auth_service.login(client=client, email=body.email, password=body.password)
    except (AuthenticationError, ValidationError):
        raise
    except Exception as exc:
        raise _to_http(exc, "Unexpected login error") from exc


@router.post("/refresh", response_model=AuthResponse)
@limiter.limit("30/minute")
def refresh(request: Request, body: RefreshRequest):
    """Refresh an access token. Public endpoint."""
    client = get_anon_client()
    try:
        return auth_service.refresh_token(
            client=client, refresh_token_value=body.refresh_token
        )
    except AuthenticationError:
        raise
    except Exception as exc:
        raise _to_http(exc, "Unexpected refresh error") from exc


@router.post("/logout")
def logout(user: dict = Depends(get_current_user)):
    """Sign out the current user."""
    client = get_supabase_client(user["access_token"])
    return auth_service.logout(client=client, access_token=user["access_token"])
