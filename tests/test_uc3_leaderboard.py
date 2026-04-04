import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

import pytest
from fantasy_leaderboard_usecase_3.leaderboard import GlobalLeaderboard
from fantasy_leaderboard_usecase_3.observers import ConsoleNotifierObserver


class TestLeaderboardSingleton:
    def test_singleton_same_instance(self):
        lb1 = GlobalLeaderboard()
        lb2 = GlobalLeaderboard()
        assert lb1 is lb2

    def test_update_team_score(self):
        lb = GlobalLeaderboard()
        lb.update_team_score(100, "Test Team", 45, 80.0)
        ranking = lb.get_sorted_leaderboard()
        assert any(t['name'] == 'Test Team' for t in ranking)

    def test_ranking_is_sorted_descending(self):
        lb = GlobalLeaderboard()
        lb.update_team_score(101, "Low Score Team", 10, 90.0)
        lb.update_team_score(102, "High Score Team", 99, 70.0)
        ranking = lb.get_sorted_leaderboard()
        scores = [t['score'] for t in ranking]
        assert scores == sorted(scores, reverse=True)

    def test_observer_notified_on_update(self, capsys):
        lb = GlobalLeaderboard()
        lb.attach(ConsoleNotifierObserver())
        lb.update_team_score(200, "Observer Test Team", 55, 75.0)
        captured = capsys.readouterr()
        assert "LEADERBOARD" in captured.out
