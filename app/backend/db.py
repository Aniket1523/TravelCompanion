from __future__ import annotations

from supabase import Client, create_client

from config import SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL


def get_supabase_client(access_token: str | None = None) -> Client:
    """Return a Supabase client scoped to the user's JWT for RLS."""
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    if access_token:
        client.postgrest.auth(access_token)
    return client


def get_service_client() -> Client:
    """Return a Supabase client with service_role key (bypasses RLS).
    Use only for privileged operations like match creation."""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
