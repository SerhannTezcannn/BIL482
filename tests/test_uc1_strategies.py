import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

import pytest
from fantasy_team_usecase_1.strategies import (
    BudgetValidation, SquadSizeValidation, PositionValidation, TeamLimitValidation
)
from fantasy_team_usecase_1.factories import PlayerFactory

def make_player(team="Arsenal", position="Midfielder", cost=7.0):
    return PlayerFactory.create_player({
        "id": 1, "first_name": "Test", "second_name": "Player",
        "team": team, "position": position, "cost": cost,
        "total_points": 0, "minutes": 90
    })

class FakeTeam:
    def __init__(self, players, total_cost):
        self.players = players
        self.total_cost = total_cost

class TestBudgetValidation:
    def test_within_budget(self):
        players = [make_player(cost=5.0) for _ in range(15)]
        team = FakeTeam(players, 75.0)
        ok, msg = BudgetValidation(100.0).validate(team)
        assert ok is True

    def test_over_budget(self):
        players = [make_player(cost=10.0) for _ in range(15)]
        team = FakeTeam(players, 150.0)
        ok, msg = BudgetValidation(100.0).validate(team)
        assert ok is False
        assert "Budget exceeded" in msg

    def test_exactly_at_budget_limit(self):
        players = [make_player(cost=6.67) for _ in range(15)]
        team = FakeTeam(players, 100.0)
        ok, msg = BudgetValidation(100.0).validate(team)
        assert ok is True


class TestSquadSizeValidation:
    def test_correct_size(self):
        players = [make_player() for _ in range(15)]
        team = FakeTeam(players, 70.0)
        ok, msg = SquadSizeValidation(15).validate(team)
        assert ok is True

    def test_too_few_players(self):
        players = [make_player() for _ in range(14)]
        team = FakeTeam(players, 65.0)
        ok, msg = SquadSizeValidation(15).validate(team)
        assert ok is False
        assert "14" in msg

    def test_too_many_players(self):
        players = [make_player() for _ in range(16)]
        team = FakeTeam(players, 75.0)
        ok, msg = SquadSizeValidation(15).validate(team)
        assert ok is False
        assert "16" in msg


class TestPositionValidation:
    def _build_valid_squad(self):
        squad = []
        squad += [make_player(position="Goalkeeper") for _ in range(2)]
        squad += [make_player(position="Defender") for _ in range(5)]
        squad += [make_player(position="Midfielder") for _ in range(5)]
        squad += [make_player(position="Forward") for _ in range(3)]
        return squad

    def test_valid_positions(self):
        team = FakeTeam(self._build_valid_squad(), 105.0)
        ok, msg = PositionValidation().validate(team)
        assert ok is True

    def test_wrong_goalkeeper_count(self):
        squad = []
        squad += [make_player(position="Goalkeeper") for _ in range(3)]
        squad += [make_player(position="Defender") for _ in range(4)]
        squad += [make_player(position="Midfielder") for _ in range(5)]
        squad += [make_player(position="Forward") for _ in range(3)]
        team = FakeTeam(squad, 105.0)
        ok, msg = PositionValidation().validate(team)
        assert ok is False
        assert "Goalkeeper" in msg


class TestTeamLimitValidation:
    def test_within_club_limit(self):
        squad = []
        clubs = ["Arsenal", "Chelsea", "Liverpool", "Spurs", "Man Utd"]
        for i, club in enumerate(clubs):
            squad += [make_player(team=club) for _ in range(3)]
        team = FakeTeam(squad, 105.0)
        ok, msg = TeamLimitValidation(3).validate(team)
        assert ok is True

    def test_exceeds_club_limit(self):
        squad = [make_player(team="Arsenal") for _ in range(4)]
        squad += [make_player(team="Chelsea") for _ in range(11)]
        team = FakeTeam(squad, 105.0)
        ok, msg = TeamLimitValidation(3).validate(team)
        assert ok is False
        assert "Arsenal" in msg
