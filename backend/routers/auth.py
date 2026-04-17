# NOTE: Do NOT add ``from __future__ import annotations`` to this router.
# When combined with ``Body(...)`` on Pydantic model parameters it produces
# ``Annotated[<str>, Body(...)]`` ForwardRefs that Pydantic cannot resolve at
# request time, breaking every endpoint here with a PydanticUserError. The
# ``Body(...)`` markers are themselves required because slowapi's
# ``@limiter.limit`` decorator perturbs the function signature enough that
# FastAPI otherwise misreads the body param as a query param (HTTP 422).
from fastapi import APIRouter, Body, Depends, HTTPException, Request

from auth import get_current_user
from db import get_anon_client, get_supabase_client
from exceptions import AuthenticationError, ConflictError, ValidationError
from logging_config import logger
from models.auth import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    ResendConfirmationRequest,
    ResendConfirmationResponse,
    SignupRequest,
)
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
def signup(request: Request, body: SignupRequest = Body(...)):
    """Register a new user. Public endpoint — no Authorization header required.
    Rate-limited to 5/min per IP to deter abuse.

    Note: explicit ``Body(...)`` is required because slowapi's ``@limiter.limit``
    wrapper perturbs the function signature just enough that FastAPI misreads
    the Pydantic body parameter as a query parameter (returning 422). Adding
    ``Body(...)`` forces FastAPI to treat it as a JSON request body.
    """
    client = get_anon_client()
    try:
        return auth_service.signup(
            client=client, email=body.email, password=body.password
        )
    except (ConflictError, AuthenticationError, ValidationError):
        raise  # domain exceptions → proper 409 / 401 / 422 with CORS headers
    except Exception as exc:
        raise _to_http(exc, "Unexpected signup error") from exc


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
def login(request: Request, body: LoginRequest = Body(...)):
    """Authenticate with email and password. Public endpoint.
    Rate-limited to 10/min per IP."""
    client = get_anon_client()
    try:
        return auth_service.login(
            client=client, email=body.email, password=body.password
        )
    except (AuthenticationError, ValidationError):
        raise
    except Exception as exc:
        raise _to_http(exc, "Unexpected login error") from exc


@router.post("/refresh", response_model=AuthResponse)
@limiter.limit("30/minute")
def refresh(request: Request, body: RefreshRequest = Body(...)):
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


@router.post("/resend-confirmation", response_model=ResendConfirmationResponse)
@limiter.limit("3/minute")
def resend_confirmation(
    request: Request, body: ResendConfirmationRequest = Body(...)
):
    """Resend the Supabase signup confirmation email. Public endpoint.

    Rate-limited to 3/min per IP to deter abuse. Always returns the same
    generic message to prevent account enumeration.
    """
    client = get_anon_client()
    try:
        return auth_service.resend_confirmation(client=client, email=body.email)
    except Exception as exc:
        raise _to_http(exc, "Unexpected resend-confirmation error") from exc
