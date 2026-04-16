from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from auth import get_current_user
from db import get_anon_client, get_supabase_client
from models.auth import AuthResponse, LoginRequest, RefreshRequest, SignupRequest
from rate_limit import limiter
from services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=201)
@limiter.limit("5/minute")
def signup(request: Request, body: SignupRequest):
    """Register a new user. Public endpoint — no Authorization header required.
    Rate-limited to 5/min per IP to deter abuse."""
    client = get_anon_client()
    return auth_service.signup(client=client, email=body.email, password=body.password)


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
def login(request: Request, body: LoginRequest):
    """Authenticate with email and password. Public endpoint.
    Rate-limited to 10/min per IP."""
    client = get_anon_client()
    return auth_service.login(client=client, email=body.email, password=body.password)


@router.post("/refresh", response_model=AuthResponse)
@limiter.limit("30/minute")
def refresh(request: Request, body: RefreshRequest):
    """Refresh an access token. Public endpoint."""
    client = get_anon_client()
    return auth_service.refresh_token(
        client=client, refresh_token_value=body.refresh_token
    )


@router.post("/logout")
def logout(user: dict = Depends(get_current_user)):
    """Sign out the current user."""
    client = get_supabase_client(user["access_token"])
    return auth_service.logout(client=client, access_token=user["access_token"])
