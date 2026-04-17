# NOTE: Do NOT add ``from __future__ import annotations`` here. It combines
# with ``Body(...)`` to produce unresolvable Annotated[ForwardRef, Body(...)]
# tuples and Pydantic raises PydanticUserError at request time. See the
# matching note in ``routers/auth.py``.
from typing import List

from fastapi import APIRouter, Body, Depends, Query, Request
from supabase import Client

from auth import get_current_user
from db import get_service_client
from dependencies import get_user_client
from models.matches import (
    MatchResponse,
    MatchRunRequest,
    MatchRunResponse,
    MatchUpdateRequest,
)
from rate_limit import limiter
from services import match_service

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/run", response_model=MatchRunResponse)
@limiter.limit("20/minute")
def run_match(
    request: Request,
    body: MatchRunRequest = Body(...),
    user: dict = Depends(get_current_user),
):
    """Trigger the matching engine for a flight.
    Uses service_role client for cross-user reads and match insertion.
    Rate-limited to 20/min per IP to prevent thrash on the engine."""
    service_client = get_service_client()
    return match_service.run_matching(
        service_client=service_client, flight_id=body.flight_id
    )


@router.get("", response_model=List[MatchResponse])
def get_matches(
    user: dict = Depends(get_current_user),
    client: Client = Depends(get_user_client),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get all matches for the authenticated user (seeker or helper)."""
    return match_service.get_user_matches(
        client=client, user_id=user["id"], limit=limit, offset=offset
    )


@router.patch("/{match_id}", response_model=MatchResponse)
def update_match(
    match_id: str,
    body: MatchUpdateRequest,
    user: dict = Depends(get_current_user),
    client: Client = Depends(get_user_client),
):
    """Update match status (accept, reject, complete)."""
    return match_service.update_match_status(
        client=client,
        user_id=user["id"],
        match_id=match_id,
        status=body.status,
    )
