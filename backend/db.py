from __future__ import annotations

from supabase import Client, create_client

from config import SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL


def get_anon_client() -> Client:
    """Return a Supabase client keyed with the anon/public key.

    Use this for ALL Supabase Auth operations (sign_up, sign_in, refresh,
    sign_out).  The anon key is intentionally public and carries no elevated
    privileges; it is the only valid key for auth.sign_up().
    """
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


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
