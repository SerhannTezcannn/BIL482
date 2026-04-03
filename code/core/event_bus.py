from collections import defaultdict
from typing import Callable, Any

class EventBus:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.subscribers = defaultdict(list)
        return cls._instance
        
    def subscribe(self, event_type: str, callback: Callable):
        if callback not in self.subscribers[event_type]:
            self.subscribers[event_type].append(callback)
        
    def publish(self, event_type: str, data: Any = None):
        print(f"[EventBus] Emitting event: {event_type}")
        for callback in self.subscribers.get(event_type, []):
            callback(data)

bus = EventBus()

class Events:
    GAMEWEEK_DATA_FETCHED = "GAMEWEEK_DATA_FETCHED"
    TEAM_SCORES_UPDATED = "TEAM_SCORES_UPDATED"
    LEADERBOARD_REFRESHED = "LEADERBOARD_REFRESHED"
