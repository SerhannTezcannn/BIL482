from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
from typing import List, Optional

# Core imports (Database and Event Bus)
from core.database import DB_NAME, get_db_connection, BASE_DIR
from core.event_bus import bus, Events

# Include Standalone Use Case Routers
from fantasy_team_usecase_1.router import router as team_router
from fantasy_leaderboard_usecase_3.router import router as leaderboard_router

# Leaderboard Singleton and Calculator
from fantasy_leaderboard_usecase_3.leaderboard import GlobalLeaderboard
from fantasy_points_usecase_2.calculator import TeamPointCalculator
from fantasy_leaderboard_usecase_3.observers import ConsoleNotifierObserver, UIEventNotifierObserver

app = FastAPI(title="Fantasy Football API - Standalone (UC1, UC2 & UC3)")

# Global Leaderboard instance
leaderboard_instance = GlobalLeaderboard()

# Adapter function for EventBus to Leaderboard
def sync_leaderboard(data: dict):
    leaderboard_instance.update_team_score(
        data['team_id'], 
        data['team_name'], 
        data['score'], 
        data.get('budget', 0)
    )

# Subscribe observers correctly (UC1 -> UC2 -> UC3 flow)
# Note: GAMEWEEK_DATA_FETCHED usually triggers UC2 which triggers TEAM_SCORES_UPDATED
bus.subscribe(Events.TEAM_SCORES_UPDATED, sync_leaderboard)
bus.subscribe(Events.LEADERBOARD_REFRESHED, ConsoleNotifierObserver().update)

# Include Routers
app.include_router(team_router)
app.include_router(leaderboard_router)

@app.on_event("startup")
def setup_on_boot():
    from database_setup import create_schema
    # Database initialization
    if not os.path.exists(DB_NAME):
        print(f"[System] Initializing Standalone Database: {DB_NAME}")
        create_schema()
    
    # Pre-load Leaderboard into memory
    print("[System] Loading Leaderboard into Memory...")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, budget_used FROM user_teams")
    teams = [dict(row) for row in c.fetchall()]
    
    calc = TeamPointCalculator()
    for t in teams:
        query = '''
            SELECT p.id, tp.is_captain, tp.is_bench, s.total_points, s.minutes, s.goals, s.assists
            FROM team_players tp
            JOIN players p ON tp.player_id = p.id
            LEFT JOIN stats s ON p.id = s.player_id AND s.gameweek = (SELECT MAX(gameweek) FROM stats)
            WHERE tp.team_id = ?
        '''
        c.execute(query, (t['id'],))
        players = [dict(row) for row in c.fetchall()]
        score = calc.calculate_team_score(players)
        
        leaderboard_instance._teams_cache[t['id']] = {
            "name": t['name'],
            "score": score,
            "budget": t['budget_used']
        }
    print(f"[System] Loaded {len(teams)} teams.")
    conn.close()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)

@app.get("/")
def read_root():
    return {
        "title": "Fantasy Football Standalone API (UC1-3)",
        "description": "Including Team Builder, Scoring Engine and Leaderboard.",
        "docs": "/docs",
        "endpoints": ["/team", "/leaderboard", "/players", "/stats/{gw}"]
    }

# --- Generic Player Access Endpoints ---

@app.get("/players")
def get_players(team: Optional[str] = None):
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
def get_gameweek_stats(gameweek: str):
    conn = get_db_connection()
    c = conn.cursor()
    gw_num = 24 if gameweek.lower() == "latest" else int(gameweek)
    query = '''
        SELECT p.first_name, p.second_name, p.team, p.position_id, p.cost, s.*
        FROM stats s
        JOIN players p ON s.player_id = p.id
        WHERE s.gameweek = ?
        ORDER BY s.total_points DESC
    '''
    c.execute(query, (gw_num,))
    stats = [dict(row) for row in c.fetchall()]
    conn.close()
    return stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
