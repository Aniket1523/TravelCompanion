"""Tests for domain exception handling in the app."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app" / "backend"))

from unittest.mock import patch

from conftest import MOCK_FLIGHT_ID

from exceptions import ConflictError, NotFoundError


@patch("routers.flights.flight_service")
def test_conflict_returns_409(mock_service, seeker_client):
    mock_service.create_or_get_flight.return_value = {
        "id": MOCK_FLIGHT_ID,
        "flight_number": "AI101",
        "source": "BLR",
        "destination": "DEL",
        "departure_date": "2026-06-15",
        "created_at": "2026-06-01T00:00:00",
    }
    mock_service.create_user_flight.side_effect = ConflictError(
        "You are already registered for this flight"
    )

    response = seeker_client.post(
        "/flights",
        json={
            "flight_number": "AI101",
            "source": "BLR",
            "destination": "DEL",
            "departure_date": "2026-06-15",
            "pnr": "PNR001",
        },
    )

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


@patch("routers.matches.get_service_client")
@patch("routers.matches.match_service")
def test_not_found_returns_404(mock_service, mock_svc_client, seeker_client):
    mock_service.run_matching.side_effect = NotFoundError("Flight not found")

    response = seeker_client.post(
        "/matches/run", json={"flight_id": "nonexistent"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Flight not found"
