from typing import Dict, Any, List
import logging
from fantasy_points_usecase_2.scoring_strategies import (
    ScoringStrategy, GoalkeeperScoringStrategy, DefenderScoringStrategy,
    MidfielderScoringStrategy, ForwardScoringStrategy, ModifierStrategy
)

logger = logging.getLogger(__name__)

class TeamPointCalculator:
    def __init__(self):
        self.strategies = {
            "Goalkeeper": GoalkeeperScoringStrategy(),
            "Defender": DefenderScoringStrategy(),
            "Midfielder": MidfielderScoringStrategy(),
            "Forward": ForwardScoringStrategy(),
            "1": GoalkeeperScoringStrategy(),
            "2": DefenderScoringStrategy(),
            "3": MidfielderScoringStrategy(),
            "4": ForwardScoringStrategy()
        }

    def calculate_team_score(self, players_data: List[Dict[str, Any]]) -> int:
        total_score = 0
        
        for player in players_data:
            for k, v in player.items():
                if v is None and k not in ['first_name', 'second_name', 'team', 'position_id', 'opponent', 'venue', 'result']:
                    player[k] = 0

            position = str(player.get("position", ""))
            
            is_bench = player.get("is_bench", False)
            is_captain = player.get("is_captain", False)
            
            strategy: ScoringStrategy = self.strategies.get(position)
            
            if not strategy:
                logger.warning(f"Unknown position '{position}' for player {player.get('name')}. Defaulting to 0 pts.")
                continue
                
            if is_bench:
                strategy = ModifierStrategy(strategy, 0)
            elif is_captain:
                strategy = ModifierStrategy(strategy, 2)
            else:
                strategy = ModifierStrategy(strategy, 1)
                
            player_score = strategy.calculate_score(player)
            total_score += player_score
            
            role = "Captain" if is_captain else ("Bench" if is_bench else "Starter")
            logger.info(f"Scored {player_score} pts for {player.get('name')} ({role} - {position})")
            
        return total_score
