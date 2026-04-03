from typing import List, Dict, Any

class GlobalLeaderboard:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GlobalLeaderboard, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._observers = []
        self._teams_cache: Dict[int, Dict[str, Any]] = {}

    def attach(self, observer: Any):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Any):
        self._observers.remove(observer)

    def notify(self):
        sorted_board = self.get_sorted_leaderboard()
        from core.event_bus import bus, Events
        bus.publish(Events.LEADERBOARD_REFRESHED, sorted_board)
        
        for observer in self._observers:
            observer.update(sorted_board)

    def update_team_score(self, team_id: int, team_name: str, score: int, budget: float = 0.0):
        changed = False
        if team_id not in self._teams_cache:
            self._teams_cache[team_id] = {"name": team_name, "score": score, "budget": budget}
            changed = True
        else:
            if self._teams_cache[team_id]["score"] != score:
                self._teams_cache[team_id]["score"] = score
                changed = True
                
        if changed:
            self.notify()

    def get_sorted_leaderboard(self) -> List[Dict[str, Any]]:
        teams_list = [{"id": tid, **data} for tid, data in self._teams_cache.items()]
        teams_list.sort(key=lambda x: (-x['score'], x['budget']))
        return teams_list
        
    def populate_initial_state(self, initial_teams: List[Dict[str, Any]]):
        for team in initial_teams:
            self._teams_cache[team['id']] = {
                "name": team['name'],
                "score": team['score'],
                "budget": team.get('budget', 0.0)
            }
