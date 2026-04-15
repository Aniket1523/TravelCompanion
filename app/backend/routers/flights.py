from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query
from supabase import Client

from auth import get_current_user
from dependencies import get_user_client
from models.flights import FlightCreate, UserFlightResponse
from services import flight_service

router = APIRouter(prefix="/flights", tags=["flights"])


@router.post("", response_model=UserFlightResponse, status_code=201)
def create_flight(
    body: FlightCreate,
    user: dict = Depends(get_current_user),
    client: Client = Depends(get_user_client),
):
    """Create or reuse a flight, then link the user to it with their PNR."""
    flight = flight_service.create_or_get_flight(
        client=client,
        flight_number=body.flight_number.upper(),
        source=body.source.upper(),
        destination=body.destination.upper(),
        departure_date=body.departure_date.isoformat(),
    )

    user_flight = flight_service.create_user_flight(
        client=client,
        user_id=user["id"],
        flight_id=flight["id"],
        pnr=body.pnr.upper(),
    )

    user_flight["flight"] = flight
    return user_flight


@router.get("", response_model=List[UserFlightResponse])
def get_flights(
    user: dict = Depends(get_current_user),
    client: Client = Depends(get_user_client),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get flights for the authenticated user (paginated)."""
    data = flight_service.get_user_flights(
        client=client, user_id=user["id"], limit=limit, offset=offset
    )
    # Reshape nested join: Supabase returns "flights" key from join
    for item in data:
        if "flights" in item:
            item["flight"] = item.pop("flights")
    return data
