from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
from typing import List, Optional

# Core imports (Database and Event Bus)
from core.database import DB_NAME, get_db_connection, BASE_DIR
from core.event_bus import bus, Events

app = FastAPI(title="Fantasy Football API - Standalone (UC1 & UC2)")

# Include Modular Use Case Routers
from fantasy_team_usecase_1.router import router as team_router

# In this standalone version, only UC1 (Team Builder) router is registered.
# Use Case 2 (Points Calculator) is currently a library used by UC1.
app.include_router(team_router)

# Note: UC3 (Leaderboard) and UC4 (Data Fetcher) routers are excluded 
# in this standalone sub-project for specific submission.

@app.on_event("startup")
def setup_on_boot():
    from database_setup import create_schema
    # Database initialization if it doesn't exist
    if not os.path.exists(DB_NAME):
        print(f"[System] Initializing Standalone Database: {DB_NAME}")
        create_schema()
    else:
        print(f"[System] Standalone Database found.")

# CORS Middleware (Useful for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """
    Root endpoint for standalone UC1 & UC2 documentation access.
    """
    return {
        "title": "Fantasy Football Standalone API",
        "description": "Covering Use Case 1: Team Builder and Use Case 2: Points Calculator",
        "docs": "/docs",
        "endpoints": ["/team", "/players", "/stats/{gw}"]
    }

# --- Generic Player Access Endpoints (Core Functionality for UC1 & UC2) ---

@app.get("/players")
def get_players(team: Optional[str] = None):
    """
    Returns list of players for team selection (UC1 requirement).
    """
    conn = get_db_connection()
    c = conn.cursor()
    query = "SELECT * FROM players"
    params = []
    if team:
        query += " WHERE team = ?"
        params.append(team)
    c.execute(query, params)
    players = [dict(row) for row in c.fetchall()]
    conn.close()
    return players

@app.get("/stats/{gameweek}")
def get_gameweek_stats(gameweek: str, sort_by: str = "total_points"):
    """
    Returns player performance stats for a specific gameweek (UC2 requirement).
    """
    conn = get_db_connection()
    c = conn.cursor()
    if gameweek.lower() == "latest":
        c.execute("SELECT MAX(gameweek) FROM stats")
        res = c.fetchone()
        gw_num = int(res[0]) if res and res[0] is not None else 24
    else:
        gw_num = int(gameweek)
        
    allowed_sort = ["total_points", "goals", "assists", "ict_index", "minutes"]
    if sort_by not in allowed_sort:
        sort_by = "total_points"
        
    query = f'''
        SELECT p.first_name, p.second_name, p.team, p.position_id, p.cost, s.*
        FROM stats s
        JOIN players p ON s.player_id = p.id
        WHERE s.gameweek = ?
        ORDER BY s.{sort_by} DESC
    '''
    c.execute(query, (gw_num,))
    stats = [dict(row) for row in c.fetchall()]
    conn.close()
    return stats

@app.get("/player/{player_id}/history")
def get_player_history(player_id: int):
    """
    Detailed history for a specific player.
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE id = ?", (player_id,))
    player = c.fetchone()
    if not player:
        conn.close()
        raise HTTPException(status_code=404, detail="Player not found")
    c.execute("SELECT * FROM stats WHERE player_id = ? ORDER BY gameweek ASC", (player_id,))
    stats = [dict(row) for row in c.fetchall()]
    conn.close()
    return {"player": dict(player), "history": stats}

if __name__ == "__main__":
    import uvicorn
    # Standalone server runs on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
