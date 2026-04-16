"""FastAPI dependencies for dependency injection."""

from __future__ import annotations

from fastapi import Depends
from supabase import Client

from auth import get_current_user
from db import get_supabase_client


def get_user_client(user: dict = Depends(get_current_user)) -> Client:
    """Return a Supabase client scoped to the authenticated user's JWT."""
    return get_supabase_client(user["access_token"])
