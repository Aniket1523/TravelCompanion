from __future__ import annotations

from supabase import Client

from exceptions import ConflictError, NotFoundError
from logging_config import logger


def create_helper_availability(
    client: Client, user_id: str, flight_id: str, is_available: bool
) -> dict:
    """Register or update helper availability for a flight."""
    existing = (
        client.table("helper_availability")
        .select("*")
        .eq("user_id", user_id)
        .eq("flight_id", flight_id)
        .execute()
    )
    if existing.data:
        raise ConflictError("You already have availability set for this flight")

    result = (
        client.table("helper_availability")
        .insert(
            {
                "user_id": user_id,
                "flight_id": flight_id,
                "is_available": is_available,
            }
        )
        .execute()
    )
    logger.info(
        "Created helper availability for user %s on flight %s",
        user_id,
        flight_id,
    )
    return result.data[0]


def update_helper_availability(
    client: Client, user_id: str, availability_id: str, is_available: bool
) -> dict:
    """Update helper availability."""
    existing = (
        client.table("helper_availability")
        .select("*")
        .eq("id", availability_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not existing.data:
        raise NotFoundError("Availability entry not found")

    result = (
        client.table("helper_availability")
        .update({"is_available": is_available})
        .eq("id", availability_id)
        .eq("user_id", user_id)
        .execute()
    )
    logger.info("Updated helper availability %s to %s", availability_id, is_available)
    return result.data[0]


def get_helper_availability(
    client: Client,
    user_id: str,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Get all availability entries for a helper."""
    result = (
        client.table("helper_availability")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return result.data
