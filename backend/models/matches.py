from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class MatchRunRequest(BaseModel):
    flight_id: str


class MatchUpdateRequest(BaseModel):
    status: Literal["accepted", "rejected", "completed"]


class MatchResponse(BaseModel):
    id: str
    seeker_id: str
    helper_id: str
    flight_id: str
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MatchRunResponse(BaseModel):
    matches_created: int
    matches: list[MatchResponse]
