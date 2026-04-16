from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query
from supabase import Client

from auth import get_current_user
from dependencies import get_user_client
from models.seeker import SeekerRequestCreate, SeekerRequestResponse
from services import seeker_service

router = APIRouter(prefix="/seeker", tags=["seeker"])


@router.post("/request", response_model=SeekerRequestResponse, status_code=201)
def create_request(
    body: SeekerRequestCreate,
    user: dict = Depends(get_current_user),
    client: Client = Depends(get_user_client),
):
    """Create a help request for a flight."""
    return seeker_service.create_seeker_request(
        client=client,
        user_id=user["id"],
        flight_id=body.flight_id,
        notes=body.notes,
    )


@router.get("/requests", response_model=List[SeekerRequestResponse])
def get_requests(
    user: dict = Depends(get_current_user),
    client: Client = Depends(get_user_client),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get all help requests for the authenticated seeker."""
    return seeker_service.get_seeker_requests(
        client=client, user_id=user["id"], limit=limit, offset=offset
    )


@router.delete("/request/{request_id}")
def cancel_request(
    request_id: str,
    user: dict = Depends(get_current_user),
    client: Client = Depends(get_user_client),
):
    """Cancel an open seeker request."""
    return seeker_service.cancel_seeker_request(
        client=client, user_id=user["id"], request_id=request_id
    )
