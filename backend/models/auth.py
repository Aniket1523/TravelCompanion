from __future__ import annotations

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str
    # True when Supabase has email confirmation enabled and the user must click
    # a link before their tokens are usable. Frontend should NOT persist the
    # empty access_token / refresh_token strings in this case.
    email_confirmation_required: bool = False


class RefreshRequest(BaseModel):
    refresh_token: str


class ResendConfirmationRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)


class ResendConfirmationResponse(BaseModel):
    message: str
