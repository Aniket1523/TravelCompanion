from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query
from supabase import Client

from auth import get_current_user
from dependencies import get_user_client
from models.helper import (
    HelperAvailabilityCreate,
    HelperAvailabilityResponse,
    HelperAvailabilityUpdate,
)
from services import helper_service

router = APIRouter(prefix="/helper", tags=["helper"])


@router.post(
    "/availability", response_model=HelperAvailabilityResponse, status_code=201
)
def create_availability(
    body: HelperAvailabilityCreate,
    user: dict = Depends(get_current_user),
    client: Client = Depends(get_user_client),
):
    """Register helper availability for a flight."""
    return helper_service.create_helper_availability(
        client=client,
        user_id=user["id"],
        flight_id=body.flight_id,
        is_available=body.is_available,
    )


@router.patch(
    "/availability/{availability_id}",
    response_model=HelperAvailabilityResponse,
)
def update_availability(
    availability_id: str,
    body: HelperAvailabilityUpdate,
    user: dict = Depends(get_current_user),
    client: Client = Depends(get_user_client),
):
    """Update helper availability."""
    return helper_service.update_helper_availability(
        client=client,
        user_id=user["id"],
        availability_id=availability_id,
        is_available=body.is_available,
    )


@router.get("/availability", response_model=List[HelperAvailabilityResponse])
def get_availability(
    user: dict = Depends(get_current_user),
    client: Client = Depends(get_user_client),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get all availability entries for the authenticated helper."""
    return helper_service.get_helper_availability(
        client=client, user_id=user["id"], limit=limit, offset=offset
    )
