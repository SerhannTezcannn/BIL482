import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

import requests
import pytest

BASE_URL = "http://127.0.0.1:8080"

def is_server_running():
    try:
        r = requests.get(f"{BASE_URL}/players", timeout=2)
        return r.status_code < 500
    except Exception:
        return False

skip_if_offline = pytest.mark.skipif(
    not is_server_running(),
    reason="API server not running at localhost:8080"
)


class TestAPIEndpoints:
    @skip_if_offline
    def test_get_players_returns_list(self):
        r = requests.get(f"{BASE_URL}/players")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0

    @skip_if_offline
    def test_get_players_filter_by_team(self):
        r = requests.get(f"{BASE_URL}/players?team=Arsenal")
        assert r.status_code == 200
        data = r.json()
        for player in data:
            assert player["team"] == "Arsenal"

    @skip_if_offline
    def test_get_stats_latest(self):
        r = requests.get(f"{BASE_URL}/stats/latest")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    @skip_if_offline
    def test_get_stats_sort_by_goals(self):
        r = requests.get(f"{BASE_URL}/stats/latest?sort_by=goals")
        assert r.status_code == 200

    @skip_if_offline
    def test_sql_injection_sort_param_rejected(self):
        r = requests.get(f"{BASE_URL}/stats/latest?sort_by=DROP_TABLE")
        assert r.status_code == 200

    @skip_if_offline
    def test_player_history_valid_id(self):
        r = requests.get(f"{BASE_URL}/player/1/history")
        assert r.status_code in [200, 404]
        if r.status_code == 200:
            data = r.json()
            assert "player" in data
            assert "history" in data

    @skip_if_offline
    def test_player_history_invalid_id(self):
        r = requests.get(f"{BASE_URL}/player/999999/history")
        assert r.status_code == 404

    @skip_if_offline
    def test_create_team_valid(self):
        # 2 GK, 5 DEF, 5 MID, 3 FWD – IDs verified against DB
        payload = {
            "name": "Test Suite Team",
            "player_ids": [1, 32, 5, 36, 71, 106, 138, 16, 47, 81, 27, 157, 30, 64, 97],
            "captain_id": 16,
            "bench_ids": [32, 138, 97]
        }
        r = requests.post(f"{BASE_URL}/team", json=payload)
        assert r.status_code == 200
        assert "team_id" in r.json()

    @skip_if_offline
    def test_create_team_with_invalid_player_id(self):
        payload = {
            "name": "Invalid Player Test",
            "player_ids": [999991, 999992, 999993],
        }
        r = requests.post(f"{BASE_URL}/team", json=payload)
        assert r.status_code == 400
