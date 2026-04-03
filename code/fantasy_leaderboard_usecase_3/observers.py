from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LeaderboardObserver(ABC):
    @abstractmethod
    def update(self, leaderboard: List[Dict[str, Any]]):
        pass

class ConsoleNotifierObserver(LeaderboardObserver):
    def update(self, leaderboard: List[Dict[str, Any]]):
        print("\n" + "="*40)
        print("🏆 LEADERBOARD UPDATED! 🏆")
        print("="*40)
        top_5 = leaderboard[:5]
        for idx, team in enumerate(top_5, 1):
            print(f"{idx}. {team['name']} - {team['score']} pts (Budget: £{team['budget']}m)")
        print("="*40 + "\n")

class UIEventNotifierObserver(LeaderboardObserver):
    def update(self, leaderboard: List[Dict[str, Any]]):
        print(f"[UI Event Notifier] Leaderboard changed. Total teams: {len(leaderboard)}. Socket push triggered.")
