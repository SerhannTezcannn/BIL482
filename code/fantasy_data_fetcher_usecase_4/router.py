from fastapi import APIRouter, HTTPException, BackgroundTasks
from core.database import DB_NAME
from core.event_bus import bus, Events
from .fetcher import GameweekDataFetcher

router = APIRouter(prefix="/admin", tags=["Data Fetcher"])
data_fetcher = GameweekDataFetcher(DB_NAME)

@router.post("/fetch-gameweek/{gameweek_id}", status_code=202)
def fetch_gameweek_data(gameweek_id: int, background_tasks: BackgroundTasks):
    """
    Production-ready endpoint: Heavy DB operations and Event triggers 
    should not block the main API thread. We delegate to a background task.
    """
    def _fetch_and_notify():
        try:
            data_fetcher.fetch_and_save_data(gameweek_id)
        except Exception as e:
            print(f"Background fetch failed: {e}")

    background_tasks.add_task(_fetch_and_notify)
    return {"message": f"GW{gameweek_id} data fetch initiated in background. EventBus will notify subscribers upon completion."}
