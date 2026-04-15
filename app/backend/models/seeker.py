from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SeekerRequestCreate(BaseModel):
    flight_id: str
    notes: str | None = Field(None, max_length=500)


class SeekerRequestResponse(BaseModel):
    id: str
    user_id: str
    flight_id: str
    notes: str | None = None
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
