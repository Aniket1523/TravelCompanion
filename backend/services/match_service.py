from __future__ import annotations

from supabase import Client

from exceptions import ConflictError, NotFoundError
from logging_config import logger


def run_matching(service_client: Client, flight_id: str) -> dict:
    """Run the v1 matching engine for a given flight.

    Uses service_role client because:
    - Needs to read seeker_requests across users
    - Needs to read helper_availability across users
    - Needs to INSERT into matches (no user-facing INSERT policy)
    """
    # Validate flight exists
    flight = service_client.table("flights").select("*").eq("id", flight_id).execute()
    if not flight.data:
        raise NotFoundError("Flight not found")

    # Get open seeker requests for this flight
    seekers = (
        service_client.table("seeker_requests")
        .select("*")
        .eq("flight_id", flight_id)
        .eq("status", "open")
        .execute()
    )

    # Get available helpers for this flight
    helpers = (
        service_client.table("helper_availability")
        .select("*")
        .eq("flight_id", flight_id)
        .eq("is_available", True)
        .execute()
    )

    if not seekers.data or not helpers.data:
        logger.info(
            "No matchable pairs for flight %s (seekers=%d, helpers=%d)",
            flight_id,
            len(seekers.data) if seekers.data else 0,
            len(helpers.data) if helpers.data else 0,
        )
        return {"matches_created": 0, "matches": []}

    # Get existing matches for this flight to avoid duplicates
    existing_matches = (
        service_client.table("matches")
        .select("seeker_id, helper_id")
        .eq("flight_id", flight_id)
        .execute()
    )
    existing_pairs = {(m["seeker_id"], m["helper_id"]) for m in existing_matches.data}

    # v1 matching: pair each unmatched seeker with the first available helper
    available_helpers = list(helpers.data)
    created_matches = []

    for seeker in seekers.data:
        for helper in available_helpers:
            # Skip self-matching
            if seeker["user_id"] == helper["user_id"]:
                continue
            # Skip if already matched
            if (seeker["user_id"], helper["user_id"]) in existing_pairs:
                continue

            match_result = (
                service_client.table("matches")
                .insert(
                    {
                        "seeker_id": seeker["user_id"],
                        "helper_id": helper["user_id"],
                        "flight_id": flight_id,
                        "status": "pending",
                    }
                )
                .execute()
            )
            created_matches.append(match_result.data[0])

            # Update seeker request status
            service_client.table("seeker_requests").update({"status": "matched"}).eq(
                "id", seeker["id"]
            ).execute()

            # Remove helper from available pool (1:1 matching)
            available_helpers.remove(helper)
            break

    logger.info(
        "Matching complete for flight %s: %d matches created",
        flight_id,
        len(created_matches),
    )
    return {"matches_created": len(created_matches), "matches": created_matches}


def get_user_matches(
    client: Client,
    user_id: str,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Get all matches for a user (as seeker or helper).
    Uses user-scoped client — RLS ensures only own matches are returned.
    Also applies explicit filter as defense-in-depth."""
    result = (
        client.table("matches")
        .select("*")
        .or_(f"seeker_id.eq.{user_id},helper_id.eq.{user_id}")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return result.data


def update_match_status(
    client: Client, user_id: str, match_id: str, status: str
) -> dict:
    """Update the status of a match (accept/reject/complete)."""
    existing = client.table("matches").select("*").eq("id", match_id).execute()
    if not existing.data:
        raise NotFoundError("Match not found")

    match = existing.data[0]
    if match["seeker_id"] != user_id and match["helper_id"] != user_id:
        raise NotFoundError("Match not found")

    valid_transitions = {
        "pending": ["accepted", "rejected"],
        "accepted": ["completed"],
    }
    current = match["status"]
    if status not in valid_transitions.get(current, []):
        raise ConflictError(f"Cannot transition match from '{current}' to '{status}'")

    result = (
        client.table("matches").update({"status": status}).eq("id", match_id).execute()
    )
    logger.info(
        "Match %s status updated: %s -> %s by user %s",
        match_id,
        current,
        status,
        user_id,
    )
    return result.data[0]
