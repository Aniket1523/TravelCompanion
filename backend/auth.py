from __future__ import annotations

from fastapi import HTTPException, Request

from db import get_supabase_client
from logging_config import logger


def get_current_user(request: Request) -> dict:
    """Extract user from Supabase JWT in Authorization header.
    Returns dict with 'id' and 'access_token'."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.removeprefix("Bearer ")
    try:
        client = get_supabase_client(token)
        user_response = client.auth.get_user(token)
        user = user_response.user
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": user.id, "access_token": token}
    except HTTPException:
        raise
    except Exception:
        token_preview = token[:10] if len(token) > 10 else "***"
        logger.warning("Auth failed for token: %s...", token_preview)
        raise HTTPException(status_code=401, detail="Invalid or expired token")
