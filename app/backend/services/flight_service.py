from __future__ import annotations

from supabase import Client

from exceptions import ConflictError
from logging_config import logger


def create_or_get_flight(
    client: Client,
    flight_number: str,
    source: str,
    destination: str,
    departure_date: str,
) -> dict:
    """Create a flight if it doesn't exist, or return the existing one."""
    existing = (
        client.table("flights")
        .select("*")
        .eq("flight_number", flight_number)
        .eq("source", source)
        .eq("destination", destination)
        .eq("departure_date", departure_date)
        .execute()
    )
    if existing.data:
        logger.debug("Flight %s already exists, reusing", flight_number)
        return existing.data[0]

    result = (
        client.table("flights")
        .insert(
            {
                "flight_number": flight_number,
                "source": source,
                "destination": destination,
                "departure_date": departure_date,
            }
        )
        .execute()
    )
    logger.info(
        "Created flight %s (%s -> %s on %s)",
        flight_number,
        source,
        destination,
        departure_date,
    )
    return result.data[0]


def create_user_flight(client: Client, user_id: str, flight_id: str, pnr: str) -> dict:
    """Link a user to a flight with their PNR."""
    existing = (
        client.table("user_flights")
        .select("*")
        .eq("user_id", user_id)
        .eq("flight_id", flight_id)
        .execute()
    )
    if existing.data:
        raise ConflictError("You are already registered for this flight")

    result = (
        client.table("user_flights")
        .insert({"user_id": user_id, "flight_id": flight_id, "pnr": pnr})
        .execute()
    )
    logger.info("Linked user %s to flight %s with PNR %s", user_id, flight_id, pnr)
    return result.data[0]


def get_user_flights(
    client: Client,
    user_id: str,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Get flights for a user (paginated), with flight details."""
    result = (
        client.table("user_flights")
        .select("*, flights(*)")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return result.data
