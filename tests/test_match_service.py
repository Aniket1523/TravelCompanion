"""Direct unit tests for the matching engine business logic."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app" / "backend"))

from exceptions import ConflictError, NotFoundError
from services.match_service import run_matching, update_match_status


def _mock_execute(data):
    """Create a mock execute() response with .data attribute."""
    result = MagicMock()
    result.data = data
    return result


def _build_chainable_table():
    """Build a chainable table mock where every method returns self."""
    table = MagicMock()
    for method in ["select", "insert", "update", "delete", "eq", "or_", "order", "range"]:
        getattr(table, method).return_value = table
    return table


def _mock_client_for_matching(
    flight_data,
    seeker_data,
    helper_data,
    existing_matches,
    insert_result=None,
):
    """Build a mock that handles the exact call sequence of run_matching."""
    client = MagicMock()
    call_index = {"n": 0}

    # run_matching calls client.table() in this order:
    # 1. flights (select)
    # 2. seeker_requests (select)
    # 3. helper_availability (select)
    # 4. matches (select existing)
    # 5. matches (insert) — per match
    # 6. seeker_requests (update) — per match
    responses = [
        flight_data,       # flights select
        seeker_data,       # seeker_requests select
        helper_data,       # helper_availability select
        existing_matches,  # matches select existing
    ]

    if insert_result:
        responses.append(insert_result)  # matches insert
        responses.append([])             # seeker_requests update

    def table_side_effect(name):
        table = _build_chainable_table()
        idx = call_index["n"]
        call_index["n"] += 1
        if idx < len(responses):
            table.execute.return_value = _mock_execute(responses[idx])
        else:
            table.execute.return_value = _mock_execute([])
        return table

    client.table.side_effect = table_side_effect
    return client


FLIGHT = {"id": "flight-1", "flight_number": "AI101"}
SEEKER_1 = {"id": "sr-1", "user_id": "user-seeker-1", "flight_id": "flight-1", "status": "open"}
SEEKER_2 = {"id": "sr-2", "user_id": "user-seeker-2", "flight_id": "flight-1", "status": "open"}
HELPER_1 = {"id": "ha-1", "user_id": "user-helper-1", "flight_id": "flight-1", "is_available": True}
HELPER_2 = {"id": "ha-2", "user_id": "user-helper-2", "flight_id": "flight-1", "is_available": True}

MATCH_1 = {
    "id": "m-1",
    "seeker_id": "user-seeker-1",
    "helper_id": "user-helper-1",
    "flight_id": "flight-1",
    "status": "pending",
    "created_at": "2026-06-01T00:00:00",
}


class TestRunMatching:
    def test_basic_1_to_1_match(self):
        client = _mock_client_for_matching(
            flight_data=[FLIGHT],
            seeker_data=[SEEKER_1],
            helper_data=[HELPER_1],
            existing_matches=[],
            insert_result=[MATCH_1],
        )
        result = run_matching(client, "flight-1")
        assert result["matches_created"] == 1
        assert result["matches"][0]["seeker_id"] == "user-seeker-1"
        assert result["matches"][0]["helper_id"] == "user-helper-1"

    def test_no_seekers(self):
        client = _mock_client_for_matching(
            flight_data=[FLIGHT],
            seeker_data=[],
            helper_data=[HELPER_1],
            existing_matches=[],
        )
        result = run_matching(client, "flight-1")
        assert result["matches_created"] == 0
        assert result["matches"] == []

    def test_no_helpers(self):
        client = _mock_client_for_matching(
            flight_data=[FLIGHT],
            seeker_data=[SEEKER_1],
            helper_data=[],
            existing_matches=[],
        )
        result = run_matching(client, "flight-1")
        assert result["matches_created"] == 0
        assert result["matches"] == []

    def test_flight_not_found(self):
        client = _mock_client_for_matching(
            flight_data=[],
            seeker_data=[],
            helper_data=[],
            existing_matches=[],
        )
        with pytest.raises(NotFoundError, match="Flight not found"):
            run_matching(client, "nonexistent-flight")

    def test_self_match_prevention(self):
        """A user who is both seeker and helper should not match with themselves."""
        same_user_seeker = {**SEEKER_1, "user_id": "user-1"}
        same_user_helper = {**HELPER_1, "user_id": "user-1"}

        client = _mock_client_for_matching(
            flight_data=[FLIGHT],
            seeker_data=[same_user_seeker],
            helper_data=[same_user_helper],
            existing_matches=[],
        )
        result = run_matching(client, "flight-1")
        assert result["matches_created"] == 0

    def test_duplicate_match_prevention(self):
        """Should not re-match an already matched seeker-helper pair."""
        existing = [{"seeker_id": "user-seeker-1", "helper_id": "user-helper-1"}]

        client = _mock_client_for_matching(
            flight_data=[FLIGHT],
            seeker_data=[SEEKER_1],
            helper_data=[HELPER_1],
            existing_matches=existing,
        )
        result = run_matching(client, "flight-1")
        assert result["matches_created"] == 0


class TestUpdateMatchStatus:
    def _mock_update_client(self, existing_match, updated_match):
        """Mock for update_match_status: first call selects, second updates."""
        client = MagicMock()
        call_index = {"n": 0}
        responses = [
            [existing_match] if existing_match else [],
            [updated_match] if updated_match else [],
        ]

        def table_side_effect(name):
            table = _build_chainable_table()
            idx = call_index["n"]
            call_index["n"] += 1
            if idx < len(responses):
                table.execute.return_value = _mock_execute(responses[idx])
            else:
                table.execute.return_value = _mock_execute([])
            return table

        client.table.side_effect = table_side_effect
        return client

    def test_valid_transition_pending_to_accepted(self):
        match = {**MATCH_1, "status": "pending"}
        updated = {**MATCH_1, "status": "accepted"}
        client = self._mock_update_client(match, updated)
        result = update_match_status(client, "user-seeker-1", "m-1", "accepted")
        assert result["status"] == "accepted"

    def test_valid_transition_pending_to_rejected(self):
        match = {**MATCH_1, "status": "pending"}
        updated = {**MATCH_1, "status": "rejected"}
        client = self._mock_update_client(match, updated)
        result = update_match_status(client, "user-helper-1", "m-1", "rejected")
        assert result["status"] == "rejected"

    def test_valid_transition_accepted_to_completed(self):
        match = {**MATCH_1, "status": "accepted"}
        updated = {**MATCH_1, "status": "completed"}
        client = self._mock_update_client(match, updated)
        result = update_match_status(client, "user-seeker-1", "m-1", "completed")
        assert result["status"] == "completed"

    def test_invalid_transition_pending_to_completed(self):
        match = {**MATCH_1, "status": "pending"}
        client = self._mock_update_client(match, None)
        with pytest.raises(ConflictError, match="Cannot transition"):
            update_match_status(client, "user-seeker-1", "m-1", "completed")

    def test_invalid_transition_rejected_to_accepted(self):
        match = {**MATCH_1, "status": "rejected"}
        client = self._mock_update_client(match, None)
        with pytest.raises(ConflictError, match="Cannot transition"):
            update_match_status(client, "user-seeker-1", "m-1", "accepted")

    def test_match_not_found(self):
        client = self._mock_update_client(None, None)
        with pytest.raises(NotFoundError, match="Match not found"):
            update_match_status(client, "user-1", "nonexistent", "accepted")

    def test_user_not_participant(self):
        match = {**MATCH_1}
        client = self._mock_update_client(match, None)
        with pytest.raises(NotFoundError, match="Match not found"):
            update_match_status(client, "user-outsider", "m-1", "accepted")
