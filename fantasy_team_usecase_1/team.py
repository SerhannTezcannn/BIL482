import logging
from fantasy_team_usecase_1.observers import Subject

logger = logging.getLogger(__name__)

class CurrentTeam(Subject):
    def __init__(self, name="My Fantasy Team"):
        super().__init__()
        self.name = name
        self.players = []
        self.total_cost = 0.0
        self.validation_strategies = []

    def add_validation_strategy(self, strategy):
        self.validation_strategies.append(strategy)

    def add_player(self, player):
        self.players.append(player)
        self.total_cost += player.cost
        self.notify(event_type="PLAYER_ADDED", player=player)

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
            self.total_cost -= player.cost
            self.notify(event_type="PLAYER_REMOVED", player=player)

    def save_team(self) -> tuple[bool, str]:
        for strategy in self.validation_strategies:
            is_valid, message = strategy.validate(self)
            if not is_valid:
                self.notify(event_type="VALIDATION_FAILED", reason=message)
                return False, message
                
        self.notify(event_type="TEAM_SAVED")
        return True, "Valid team"
