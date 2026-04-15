from __future__ import annotations

from supabase import Client

from exceptions import ConflictError, NotFoundError
from logging_config import logger


def create_seeker_request(
    client: Client, user_id: str, flight_id: str, notes: str | None
) -> dict:
    """Create a seeker help request for a flight."""
    existing = (
        client.table("seeker_requests")
        .select("*")
        .eq("user_id", user_id)
        .eq("flight_id", flight_id)
        .eq("status", "open")
        .execute()
    )
    if existing.data:
        raise ConflictError("You already have an open request for this flight")

    result = (
        client.table("seeker_requests")
        .insert({"user_id": user_id, "flight_id": flight_id, "notes": notes})
        .execute()
    )
    logger.info("Created seeker request for user %s on flight %s", user_id, flight_id)
    return result.data[0]


def get_seeker_requests(
    client: Client,
    user_id: str,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Get all seeker requests for a user."""
    result = (
        client.table("seeker_requests")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return result.data


def cancel_seeker_request(client: Client, user_id: str, request_id: str) -> dict:
    """Cancel an open seeker request."""
    existing = (
        client.table("seeker_requests")
        .select("*")
        .eq("id", request_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not existing.data:
        raise NotFoundError("Seeker request not found")

    if existing.data[0]["status"] != "open":
        raise ConflictError("Only open requests can be cancelled")

    client.table("seeker_requests").delete().eq("id", request_id).execute()
    logger.info("Cancelled seeker request %s for user %s", request_id, user_id)
    return {"id": request_id, "status": "cancelled"}
