from unittest.mock import patch

from conftest import MOCK_FLIGHT_ID, MOCK_SEEKER


@patch("routers.flights.flight_service")
def test_create_flight(mock_service, seeker_client):
    mock_service.create_or_get_flight.return_value = {
        "id": MOCK_FLIGHT_ID,
        "flight_number": "AI101",
        "source": "BLR",
        "destination": "DEL",
        "departure_date": "2026-06-15",
        "created_at": "2026-06-01T00:00:00",
    }
    mock_service.create_user_flight.return_value = {
        "id": "uf-001",
        "user_id": MOCK_SEEKER["id"],
        "flight_id": MOCK_FLIGHT_ID,
        "pnr": "PNR001",
        "created_at": "2026-06-01T00:00:00",
    }

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

    assert response.status_code == 201
    data = response.json()
    assert data["pnr"] == "PNR001"
    assert data["flight"]["flight_number"] == "AI101"


@patch("routers.flights.flight_service")
def test_get_flights(mock_service, seeker_client):
    mock_service.get_user_flights.return_value = [
        {
            "id": "uf-001",
            "user_id": MOCK_SEEKER["id"],
            "flight_id": MOCK_FLIGHT_ID,
            "pnr": "PNR001",
            "created_at": "2026-06-01T00:00:00",
            "flights": {
                "id": MOCK_FLIGHT_ID,
                "flight_number": "AI101",
                "source": "BLR",
                "destination": "DEL",
                "departure_date": "2026-06-15",
                "created_at": "2026-06-01T00:00:00",
            },
        }
    ]

    response = seeker_client.get("/flights")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["flight"]["flight_number"] == "AI101"


def test_create_flight_invalid_body(seeker_client):
    response = seeker_client.post("/flights", json={})
    assert response.status_code == 422


@patch("routers.flights.flight_service")
def test_get_flights_with_pagination(mock_service, seeker_client):
    mock_service.get_user_flights.return_value = []
    response = seeker_client.get("/flights?limit=10&offset=0")
    assert response.status_code == 200
    assert response.json() == []
