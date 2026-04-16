import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app" / "backend"))

from auth import get_current_user
from dependencies import get_user_client
from main import app

MOCK_SEEKER = {"id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "access_token": "fake"}
MOCK_HELPER = {"id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", "access_token": "fake"}
MOCK_FLIGHT_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"


def _override_user(user_data: dict):
    def override():
        return user_data

    return override


def _override_client():
    return MagicMock()


@pytest.fixture
def seeker_client():
    app.dependency_overrides[get_current_user] = _override_user(MOCK_SEEKER)
    app.dependency_overrides[get_user_client] = _override_client
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def helper_client():
    app.dependency_overrides[get_current_user] = _override_user(MOCK_HELPER)
    app.dependency_overrides[get_user_client] = _override_client
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)
