from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class FlightCreate(BaseModel):
    flight_number: str = Field(..., min_length=2, max_length=10)
    source: str = Field(..., min_length=2, max_length=10)
    destination: str = Field(..., min_length=2, max_length=10)
    departure_date: date
    pnr: str = Field(..., min_length=3, max_length=20)


class FlightResponse(BaseModel):
    id: str
    flight_number: str
    source: str
    destination: str
    departure_date: date
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserFlightCreate(BaseModel):
    flight_id: str
    pnr: str = Field(..., min_length=3, max_length=20)


class UserFlightResponse(BaseModel):
    id: str
    user_id: str
    flight_id: str
    pnr: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    flight: FlightResponse | None = None
