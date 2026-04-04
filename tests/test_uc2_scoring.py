import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

import pytest
from fantasy_points_usecase_2.scoring_strategies import (
    GoalkeeperScoringStrategy, DefenderScoringStrategy,
    MidfielderScoringStrategy, ForwardScoringStrategy, ModifierStrategy
)

class TestGoalkeeperScoring:
    def setup_method(self):
        self.strategy = GoalkeeperScoringStrategy()

    def test_no_minutes_returns_zero(self):
        stats = {"minutes": 0}
        assert self.strategy.calculate_score(stats) == 0

    def test_clean_sheet_60_plus_minutes(self):
        stats = {"minutes": 90, "clean_sheets": 1, "saves": 0, "goals_conceded": 0,
                 "goals": 0, "assists": 0, "yellow_cards": 0, "red_cards": 0, "bonus": 0, "venue": "Home"}
        assert self.strategy.calculate_score(stats) == 6  # 2 (mins) + 4 (CS)

    def test_away_clean_sheet_bonus(self):
        stats = {"minutes": 90, "clean_sheets": 1, "saves": 0, "goals_conceded": 0,
                 "goals": 0, "assists": 0, "yellow_cards": 0, "red_cards": 0, "bonus": 0, "venue": "Away"}
        assert self.strategy.calculate_score(stats) == 8  # 2 + 4 + 2

    def test_saves_points(self):
        stats = {"minutes": 90, "clean_sheets": 0, "saves": 6, "goals_conceded": 0,
                 "goals": 0, "assists": 0, "yellow_cards": 0, "red_cards": 0, "bonus": 0, "venue": "Home"}
        assert self.strategy.calculate_score(stats) == 6  # 2 (min) + 2 (6//3) + 2 (>=5 saves bonus)

    def test_yellow_card_deduction(self):
        stats = {"minutes": 90, "clean_sheets": 0, "saves": 0, "goals_conceded": 0,
                 "goals": 0, "assists": 0, "yellow_cards": 1, "red_cards": 0, "bonus": 0, "venue": "Home"}
        assert self.strategy.calculate_score(stats) == 1  # 2 - 1

    def test_red_card_deduction(self):
        stats = {"minutes": 90, "clean_sheets": 0, "saves": 0, "goals_conceded": 0,
                 "goals": 0, "assists": 0, "yellow_cards": 0, "red_cards": 1, "bonus": 0, "venue": "Home"}
        assert self.strategy.calculate_score(stats) == -1  # 2 - 3


class TestMidfielderScoring:
    def setup_method(self):
        self.strategy = MidfielderScoringStrategy()

    def test_goal_scoring(self):
        stats = {"minutes": 90, "goals": 1, "assists": 0, "clean_sheets": 0,
                 "yellow_cards": 0, "red_cards": 0, "bonus": 0, "ict_index": 0.0}
        assert self.strategy.calculate_score(stats) == 7  # 2 + 5

    def test_assist_scoring(self):
        stats = {"minutes": 90, "goals": 0, "assists": 1, "clean_sheets": 0,
                 "yellow_cards": 0, "red_cards": 0, "bonus": 0, "ict_index": 0.0}
        assert self.strategy.calculate_score(stats) == 5  # 2 + 3

    def test_full_game_high_ict_bonus(self):
        stats = {"minutes": 90, "goals": 0, "assists": 0, "clean_sheets": 0,
                 "yellow_cards": 0, "red_cards": 0, "bonus": 0, "ict_index": 9.5}
        assert self.strategy.calculate_score(stats) == 4  # 2 + 2

    def test_none_ict_handled(self):
        stats = {"minutes": 90, "goals": 0, "assists": 0, "clean_sheets": 0,
                 "yellow_cards": 0, "red_cards": 0, "bonus": 0, "ict_index": None}
        assert self.strategy.calculate_score(stats) == 2  # No crash


class TestForwardScoring:
    def setup_method(self):
        self.strategy = ForwardScoringStrategy()

    def test_hat_trick(self):
        stats = {"minutes": 90, "goals": 3, "assists": 0,
                 "yellow_cards": 0, "red_cards": 0, "bonus": 0, "ict_index": 0.0}
        assert self.strategy.calculate_score(stats) == 14  # 2 + 12

    def test_no_goal_high_ict_bonus(self):
        stats = {"minutes": 90, "goals": 0, "assists": 0,
                 "yellow_cards": 0, "red_cards": 0, "bonus": 0, "ict_index": 11.0}
        assert self.strategy.calculate_score(stats) == 5  # 2 + 3


class TestModifierStrategy:
    def test_captain_doubles_score(self):
        base = MidfielderScoringStrategy()
        captain = ModifierStrategy(base, 2)
        stats = {"minutes": 90, "goals": 1, "assists": 0, "clean_sheets": 0,
                 "yellow_cards": 0, "red_cards": 0, "bonus": 0, "ict_index": 0.0}
        assert captain.calculate_score(stats) == 14  # 7 * 2

    def test_bench_returns_zero(self):
        base = MidfielderScoringStrategy()
        bench = ModifierStrategy(base, 0)
        stats = {"minutes": 90, "goals": 2, "assists": 1, "clean_sheets": 0,
                 "yellow_cards": 0, "red_cards": 0, "bonus": 0, "ict_index": 0.0}
        assert bench.calculate_score(stats) == 0
