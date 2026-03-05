from abc import ABC, abstractmethod

class Player(ABC):
    def __init__(self, id: int, name: str, team: str, cost: float, position: str, total_points: int, minutes: int):
        self.id = id
        self.name = name
        self.team = team
        self.cost = cost
        self.position = position
        self.total_points = total_points
        self.minutes = minutes

    @abstractmethod
    def display_info(self) -> str:
        pass
        
    @abstractmethod
    def get_special_trait(self) -> str:
        pass

class Goalkeeper(Player):
    def __init__(self, id: int, name: str, team: str, cost: float, total_points: int, minutes: int, saves: int = 0, clean_sheets: int = 0, goals_conceded: int = 0):
        super().__init__(id, name, team, cost, "Goalkeeper", total_points, minutes)
        self.saves = saves
        self.clean_sheets = clean_sheets
        self.goals_conceded = goals_conceded

    def display_info(self) -> str:
        return f"[GK] {self.name} ({self.team}) | £{self.cost}m | Pts: {self.total_points} | {self.get_special_trait()}"
        
    def get_special_trait(self) -> str:
        return f"Saves: {self.saves} | CS: {self.clean_sheets} | GC: {self.goals_conceded}"

class Defender(Player):
    def __init__(self, id: int, name: str, team: str, cost: float, total_points: int, minutes: int, clean_sheets: int = 0, goals_conceded: int = 0, threat: float = 0.0):
        super().__init__(id, name, team, cost, "Defender", total_points, minutes)
        self.clean_sheets = clean_sheets
        self.goals_conceded = goals_conceded
        self.threat = threat

    def display_info(self) -> str:
        return f"[DEF] {self.name} ({self.team}) | £{self.cost}m | Pts: {self.total_points} | {self.get_special_trait()}"
        
    def get_special_trait(self) -> str:
        return f"CS: {self.clean_sheets} | GC: {self.goals_conceded} | Threat: {self.threat}"

class Midfielder(Player):
    def __init__(self, id: int, name: str, team: str, cost: float, total_points: int, minutes: int, goals: int = 0, assists: int = 0, creativity: float = 0.0):
        super().__init__(id, name, team, cost, "Midfielder", total_points, minutes)
        self.goals = goals
        self.assists = assists
        self.creativity = creativity

    def display_info(self) -> str:
        return f"[MID] {self.name} ({self.team}) | £{self.cost}m | Pts: {self.total_points} | {self.get_special_trait()}"

    def get_special_trait(self) -> str:
        return f"G: {self.goals} | A: {self.assists} | Creativity: {self.creativity}"

class Forward(Player):
    def __init__(self, id: int, name: str, team: str, cost: float, total_points: int, minutes: int, goals: int = 0, assists: int = 0, threat: float = 0.0, influence: float = 0.0):
        super().__init__(id, name, team, cost, "Forward", total_points, minutes)
        self.goals = goals
        self.assists = assists
        self.threat = threat
        self.influence = influence

    def display_info(self) -> str:
        return f"[FWD] {self.name} ({self.team}) | £{self.cost}m | Pts: {self.total_points} | {self.get_special_trait()}"

    def get_special_trait(self) -> str:
        return f"G: {self.goals} | A: {self.assists} | Threat: {self.threat} | Influence: {self.influence}"
