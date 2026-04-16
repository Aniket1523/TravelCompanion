from unittest.mock import patch

from conftest import MOCK_FLIGHT_ID, MOCK_SEEKER


@patch("routers.seeker.seeker_service")
def test_create_seeker_request(mock_service, seeker_client):
    mock_service.create_seeker_request.return_value = {
        "id": "sr-001",
        "user_id": MOCK_SEEKER["id"],
        "flight_id": MOCK_FLIGHT_ID,
        "notes": "Need help at airport",
        "status": "open",
        "created_at": "2026-06-01T00:00:00",
    }

    response = seeker_client.post(
        "/seeker/request",
        json={"flight_id": MOCK_FLIGHT_ID, "notes": "Need help at airport"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "open"
    assert data["notes"] == "Need help at airport"


@patch("routers.seeker.seeker_service")
def test_get_seeker_requests(mock_service, seeker_client):
    mock_service.get_seeker_requests.return_value = [
        {
            "id": "sr-001",
            "user_id": MOCK_SEEKER["id"],
            "flight_id": MOCK_FLIGHT_ID,
            "notes": "Need help at airport",
            "status": "open",
            "created_at": "2026-06-01T00:00:00",
        }
    ]

    response = seeker_client.get("/seeker/requests")
    assert response.status_code == 200
    assert len(response.json()) == 1


@patch("routers.seeker.seeker_service")
def test_cancel_seeker_request(mock_service, seeker_client):
    mock_service.cancel_seeker_request.return_value = {
        "id": "sr-001",
        "status": "cancelled",
    }

    response = seeker_client.delete("/seeker/request/sr-001")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
