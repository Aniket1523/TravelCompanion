from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class HelperAvailabilityCreate(BaseModel):
    flight_id: str
    is_available: bool = True


class HelperAvailabilityUpdate(BaseModel):
    is_available: bool


class HelperAvailabilityResponse(BaseModel):
    id: str
    user_id: str
    flight_id: str
    is_available: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
