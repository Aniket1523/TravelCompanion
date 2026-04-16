from unittest.mock import patch

from conftest import MOCK_FLIGHT_ID, MOCK_HELPER


@patch("routers.helper.helper_service")
def test_create_helper_availability(mock_service, helper_client):
    mock_service.create_helper_availability.return_value = {
        "id": "ha-001",
        "user_id": MOCK_HELPER["id"],
        "flight_id": MOCK_FLIGHT_ID,
        "is_available": True,
        "created_at": "2026-06-01T00:00:00",
    }

    response = helper_client.post(
        "/helper/availability",
        json={"flight_id": MOCK_FLIGHT_ID, "is_available": True},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["is_available"] is True


@patch("routers.helper.helper_service")
def test_get_helper_availability(mock_service, helper_client):
    mock_service.get_helper_availability.return_value = [
        {
            "id": "ha-001",
            "user_id": MOCK_HELPER["id"],
            "flight_id": MOCK_FLIGHT_ID,
            "is_available": True,
            "created_at": "2026-06-01T00:00:00",
        }
    ]

    response = helper_client.get("/helper/availability")
    assert response.status_code == 200
    assert len(response.json()) == 1


@patch("routers.helper.helper_service")
def test_update_helper_availability(mock_service, helper_client):
    mock_service.update_helper_availability.return_value = {
        "id": "ha-001",
        "user_id": MOCK_HELPER["id"],
        "flight_id": MOCK_FLIGHT_ID,
        "is_available": False,
        "created_at": "2026-06-01T00:00:00",
    }

    response = helper_client.patch(
        "/helper/availability/ha-001",
        json={"is_available": False},
    )

    assert response.status_code == 200
    assert response.json()["is_available"] is False
