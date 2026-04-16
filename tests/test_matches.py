from unittest.mock import patch

from conftest import MOCK_FLIGHT_ID, MOCK_HELPER, MOCK_SEEKER


@patch("routers.matches.get_service_client")
@patch("routers.matches.match_service")
def test_run_match(mock_service, mock_svc_client, seeker_client):
    mock_service.run_matching.return_value = {
        "matches_created": 1,
        "matches": [
            {
                "id": "m-001",
                "seeker_id": MOCK_SEEKER["id"],
                "helper_id": MOCK_HELPER["id"],
                "flight_id": MOCK_FLIGHT_ID,
                "status": "pending",
                "created_at": "2026-06-01T00:00:00",
            }
        ],
    }

    response = seeker_client.post(
        "/matches/run", json={"flight_id": MOCK_FLIGHT_ID}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["matches_created"] == 1
    assert data["matches"][0]["seeker_id"] == MOCK_SEEKER["id"]
    assert data["matches"][0]["helper_id"] == MOCK_HELPER["id"]


@patch("routers.matches.get_service_client")
@patch("routers.matches.match_service")
def test_run_match_no_helpers(mock_service, mock_svc_client, seeker_client):
    mock_service.run_matching.return_value = {
        "matches_created": 0,
        "matches": [],
    }

    response = seeker_client.post(
        "/matches/run", json={"flight_id": MOCK_FLIGHT_ID}
    )

    assert response.status_code == 200
    assert response.json()["matches_created"] == 0


@patch("routers.matches.match_service")
def test_get_matches_as_seeker(mock_service, seeker_client):
    mock_service.get_user_matches.return_value = [
        {
            "id": "m-001",
            "seeker_id": MOCK_SEEKER["id"],
            "helper_id": MOCK_HELPER["id"],
            "flight_id": MOCK_FLIGHT_ID,
            "status": "pending",
            "created_at": "2026-06-01T00:00:00",
        }
    ]

    response = seeker_client.get("/matches")
    assert response.status_code == 200
    assert len(response.json()) == 1


@patch("routers.matches.match_service")
def test_get_matches_as_helper(mock_service, helper_client):
    mock_service.get_user_matches.return_value = [
        {
            "id": "m-001",
            "seeker_id": MOCK_SEEKER["id"],
            "helper_id": MOCK_HELPER["id"],
            "flight_id": MOCK_FLIGHT_ID,
            "status": "pending",
            "created_at": "2026-06-01T00:00:00",
        }
    ]

    response = helper_client.get("/matches")
    assert response.status_code == 200
    assert len(response.json()) == 1


@patch("routers.matches.match_service")
def test_update_match_status(mock_service, seeker_client):
    mock_service.update_match_status.return_value = {
        "id": "m-001",
        "seeker_id": MOCK_SEEKER["id"],
        "helper_id": MOCK_HELPER["id"],
        "flight_id": MOCK_FLIGHT_ID,
        "status": "accepted",
        "created_at": "2026-06-01T00:00:00",
    }

    response = seeker_client.patch(
        "/matches/m-001", json={"status": "accepted"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
