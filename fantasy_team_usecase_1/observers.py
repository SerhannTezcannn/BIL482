import logging
from abc import ABC, abstractmethod
from typing import Any, List

logger = logging.getLogger(__name__)

class Observer(ABC):
    @abstractmethod
    def update(self, subject: Any, event_type: str, **kwargs: Any) -> None:
        pass

class Subject(ABC):
    def __init__(self) -> None:
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event_type: str, **kwargs: Any) -> None:
        for observer in self._observers:
            observer.update(self, event_type, **kwargs)

class RealTimeUIUpdater(Observer):
    def update(self, subject: Any, event_type: str, **kwargs: Any) -> None:
        if event_type == "PLAYER_ADDED":
            player = kwargs.get("player")
            if player:
                logger.info(f"[UI] SUCCESS - Added {player.name} (£{player.cost:.1f}m). Slots: {len(subject.players)}/15 | Rem. Budget: £{100.0 - subject.total_cost:.1f}m")
        elif event_type == "PLAYER_REMOVED":
            player = kwargs.get("player")
            if player:
                logger.info(f"[UI] WARNING - Removed {player.name}. Rem. Budget: £{100.0 - subject.total_cost:.1f}m")
        elif event_type == "VALIDATION_FAILED":
            reason = kwargs.get("reason", "Unknown")
            logger.error(f"[UI] ERROR - Squad Invalid: {reason}")
        elif event_type == "TEAM_SAVED":
            logger.info(f"[UI] SUCCESS - Team '{subject.name}' securely saved to database.")
