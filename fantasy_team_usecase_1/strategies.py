from abc import ABC, abstractmethod
from typing import Tuple

class ValidationStrategy(ABC):
    @abstractmethod
    def validate(self, team) -> Tuple[bool, str]:
        pass

class BudgetValidation(ValidationStrategy):
    def __init__(self, max_budget: float = 100.0):
        self.max_budget = max_budget

    def validate(self, team) -> Tuple[bool, str]:
        if team.total_cost > self.max_budget:
            return False, f"Budget exceeded: £{team.total_cost:.1f}m (Max: £{self.max_budget:.1f}m)"
        return True, "Valid budget"

class SquadSizeValidation(ValidationStrategy):
    def __init__(self, target_size: int = 15):
        self.target_size = target_size

    def validate(self, team) -> Tuple[bool, str]:
        current_size = len(team.players)
        if current_size != self.target_size:
            return False, f"Invalid squad size: {current_size} (Required: {self.target_size})"
        return True, "Valid squad size"

class PositionValidation(ValidationStrategy):
    def __init__(self, required_positions: dict = None):
        self.required_positions = required_positions or {
            "Goalkeeper": 2, # 2 GKs
            "Defender": 5, # 5 DEFs
            "Midfielder": 5, # 5 MIDs
            "Forward": 3  # 3 FWDs
        }

    def validate(self, team) -> Tuple[bool, str]:
        counts = {"Goalkeeper": 0, "Defender": 0, "Midfielder": 0, "Forward": 0}
        
        for player in team.players:
            if player.position in counts:
                counts[player.position] += 1
                
        for pos, required in self.required_positions.items():
            if counts.get(pos, 0) != required:
                return False, f"Invalid position requirement for '{pos}': {counts.get(pos, 0)} (Required: {required})"
        
        return True, "Valid positions"

class TeamLimitValidation(ValidationStrategy):
    def __init__(self, max_players_per_team: int = 3):
        self.max_players_per_team = max_players_per_team

    def validate(self, team) -> Tuple[bool, str]:
        team_counts = {}
        for player in team.players:
            team_name = player.team
            team_counts[team_name] = team_counts.get(team_name, 0) + 1
            if team_counts[team_name] > self.max_players_per_team:
                return False, f"Too many players from '{team_name}': {team_counts[team_name]} (Max: {self.max_players_per_team})"
        
        return True, "Valid team limits"
