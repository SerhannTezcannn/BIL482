from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import sqlite3
from typing import List, Optional
import os

from core.database import DB_NAME, get_db_connection, BASE_DIR

app = FastAPI(title="Fantasy Football API")

from fantasy_team_usecase_1.router import router as team_router
from fantasy_leaderboard_usecase_3.router import router as leaderboard_router
from fantasy_data_fetcher_usecase_4.router import router as fetcher_router

app.include_router(team_router)
app.include_router(leaderboard_router)
app.include_router(fetcher_router)

from fantasy_leaderboard_usecase_3.leaderboard import GlobalLeaderboard
from fantasy_points_usecase_2.calculator import TeamPointCalculator
from core.event_bus import bus, Events
from fantasy_leaderboard_usecase_3.observers import ConsoleNotifierObserver, UIEventNotifierObserver
from fantasy_data_fetcher_usecase_4.observers import TeamScoreUpdaterObserver

leaderboard = GlobalLeaderboard()

def sync_leaderboard_with_events(data: dict):
    leaderboard.update_team_score(data['team_id'], data['team_name'], data['score'], data['budget'])

bus.subscribe(Events.GAMEWEEK_DATA_FETCHED, TeamScoreUpdaterObserver(DB_NAME).update)
bus.subscribe(Events.TEAM_SCORES_UPDATED, sync_leaderboard_with_events)
bus.subscribe(Events.LEADERBOARD_REFRESHED, ConsoleNotifierObserver().update)
bus.subscribe(Events.LEADERBOARD_REFRESHED, UIEventNotifierObserver().update)

@app.on_event("startup")
def load_leaderboard():
    from database_setup import create_schema
    create_schema()
    
    print("[System] Loading Leaderboard into Memory...")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, budget_used FROM user_teams")
    teams = [dict(row) for row in c.fetchall()]
    
    calc = TeamPointCalculator()
    for t in teams:
        query = '''
            SELECT p.id, p.position_id as position, 
                   s.total_points, s.minutes, s.saves, s.clean_sheets, s.goals_conceded,
                   s.goals, s.assists, s.yellow_cards, s.red_cards, s.bonus, s.ict_index,
                   s.result, s.venue, tp.is_captain, tp.is_bench
            FROM team_players tp
            JOIN players p ON tp.player_id = p.id
            LEFT JOIN stats s ON p.id = s.player_id AND s.gameweek = (SELECT MAX(gameweek) FROM stats)
            WHERE tp.team_id = ?
        '''
        c.execute(query, (t['id'],))
        players = [dict(row) for row in c.fetchall()]
        score: int = calc.calculate_team_score(players)
        
        leaderboard._teams_cache[t['id']] = {
            "name": t['name'],
            "score": score,
            "budget": t['budget_used']
        }
    print(f"[System] Loaded {len(teams)} teams into Global Leaderboard.")
    conn.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        index_path = os.path.join(BASE_DIR, "frontend", "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[Error serving index.html]: {e}")
        raise HTTPException(status_code=500, detail=f"File read error: {e}")



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
def get_gameweek_stats(gameweek: str, sort_by: str = "total_points"):
    conn = get_db_connection()
    c = conn.cursor()
    
    if gameweek.lower() == "latest":
        c.execute("SELECT MAX(gameweek) FROM stats")
        latest_gw_row = c.fetchone()
        gw_num = int(latest_gw_row[0]) if latest_gw_row and latest_gw_row[0] is not None else 24
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
    uvicorn.run(app, host="0.0.0.0", port=8080)
